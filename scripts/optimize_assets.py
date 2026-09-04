from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, Optional, Tuple

from PIL import Image

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    try:
        pillow_heif.register_avif_opener()
    except Exception:
        pass
except ImportError:
    pass

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
INPUT_DIR = PROJECT_ROOT / "img" / "projects"
OUTPUT_DIR = PROJECT_ROOT / "img" / "optimized" / "projects"
MANIFEST_PATH = PROJECT_ROOT / "node_modules" / ".cache" / "optimize-assets-manifest.json"

FFMPEG = str(PROJECT_ROOT / "ffmpeg")
FFPROBE = str(PROJECT_ROOT / "ffprobe")

RASTER_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".heic", ".heif"}
NATIVE_EXTS = {".webp", ".avif"}
VIDEO_EXTS = {".gif", ".mp4", ".mov", ".avi", ".mkv", ".m4v", ".webm"}

KEEP_ORIGINAL_PATHS = {
    "graphic-design/11.png",
    "graphic-design/12.png",
    "graphic-design/13.png",
    "graphic-design/14.png",
}

WEBP_QUALITY = 95
WEBP_METHOD = 6

VIDEO_CODEC = "libvpx-vp9"
VIDEO_CRF = 30
VIDEO_PIX_FMT = "yuv420p"
VIDEO_AUDIO_CODEC = "libopus"
VIDEO_BITRATE_MODE = "0"
VIDEO_CONTAINER_FORMAT = "webm"
FFMPEG_THREADS = "1"

MAX_WORKERS = max(1, (os.cpu_count() or 4) // 2)

POLL_INTERVAL_SECONDS = 0.05
MAX_SOURCE_POLLS = 5
MIN_STABLE_AGE_NS = 200_000_000

manifest_lock = threading.Lock()


@dataclass(frozen=True)
class SourceMeta:
    size: int
    mtime_ns: int


@dataclass(frozen=True)
class Job:
    source: Path
    destination: Path
    kind: str
    key: str


@dataclass
class JobResult:
    status: str
    job: Job
    reason: str = ""
    source_meta: Optional[SourceMeta] = None


def source_meta_to_dict(meta: SourceMeta) -> Dict[str, int]:
    return {"size": meta.size, "mtime_ns": meta.mtime_ns}


def get_source_meta(path: Path) -> SourceMeta:
    st = path.stat()
    return SourceMeta(size=st.st_size, mtime_ns=st.st_mtime_ns)


def wait_for_source_ready(path: Path) -> Tuple[bool, Optional[SourceMeta], str]:
    previous: Optional[SourceMeta] = None
    last_error = ""

    for attempt in range(MAX_SOURCE_POLLS):
        try:
            meta = get_source_meta(path)
            if meta.size <= 0:
                return False, None, "source is zero-byte"

            now_ns = time.time_ns()
            age_ns = max(0, now_ns - meta.mtime_ns)

            if age_ns >= MIN_STABLE_AGE_NS:
                return True, meta, ""

            if previous is not None:
                if previous == meta:
                    return True, meta, ""
                return False, None, "source metadata changed while waiting for stability"

            previous = meta
            last_error = "source appears recently modified; polling for stability"
        except (FileNotFoundError, PermissionError, OSError) as exc:
            last_error = f"cannot stat source: {exc}"

        if attempt < MAX_SOURCE_POLLS - 1:
            time.sleep(POLL_INTERVAL_SECONDS)

    if previous is not None and previous.size > 0:
        return True, previous, ""

    return False, None, last_error or "source metadata did not stabilize"


def is_valid_webp(path: Path) -> bool:
    try:
        with Image.open(path) as image:
            image.verify()
        return True
    except Exception:
        return False


def is_valid_webm(path: Path) -> bool:
    cmd = [
        FFPROBE,
        "-v", "error",
        "-show_entries", "format=format_name:stream=codec_type",
        "-of", "json",
        str(path),
    ]
    try:
        completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
        data = json.loads(completed.stdout or "{}")
        format_name = ((data.get("format") or {}).get("format_name") or "").lower()
        format_names = {item.strip() for item in format_name.split(",") if item.strip()}
        streams = data.get("streams") or []
        has_video_stream = any((stream or {}).get("codec_type") == "video" for stream in streams)
        return "webm" in format_names and has_video_stream
    except Exception:
        return False


def validate_output(path: Path, kind: str) -> bool:
    if not path.exists() or path.stat().st_size <= 0:
        return False
    if kind == "raster":
        return is_valid_webp(path)
    if kind == "native":
        return path.stat().st_size > 0
    if kind == "video":
        return is_valid_webm(path)
    return False


def is_stale_output(path: Path, source_meta: SourceMeta) -> bool:
    try:
        return path.stat().st_mtime_ns < source_meta.mtime_ns
    except (FileNotFoundError, PermissionError, OSError):
        return True


def build_signatures() -> Dict[str, Dict[str, str]]:
    return {
        "raster": {
            "format": "webp",
            "webp_quality": str(WEBP_QUALITY),
            "webp_method": str(WEBP_METHOD),
        },
        "native": {
            "format": "copy",
        },
        "video": {
            "container": VIDEO_CONTAINER_FORMAT,
            "video_codec": VIDEO_CODEC,
            "video_crf": str(VIDEO_CRF),
            "video_pix_fmt": VIDEO_PIX_FMT,
            "audio_codec": VIDEO_AUDIO_CODEC,
            "video_bitrate_mode": VIDEO_BITRATE_MODE,
            "ffmpeg_threads": FFMPEG_THREADS,
        },
    }


def load_manifest(path: Path) -> Dict[str, Dict[str, object]]:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
        if isinstance(raw, dict) and isinstance(raw.get("entries"), dict):
            return raw["entries"]
    except (json.JSONDecodeError, OSError, ValueError):
        print(f"warning: manifest '{path}' is corrupt; starting fresh")
    return {}


def write_manifest_atomic(path: Path, entries: Dict[str, Dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"entries": entries}
    temp_name: Optional[str] = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=".optimize-assets-manifest-",
            suffix=".tmp",
            delete=False,
        ) as tmp:
            json.dump(payload, tmp, ensure_ascii=False, indent=2, sort_keys=True)
            tmp.flush()
            os.fsync(tmp.fileno())
            temp_name = tmp.name
        os.replace(temp_name, path)
    finally:
        if temp_name and os.path.exists(temp_name):
            try:
                os.unlink(temp_name)
            except OSError:
                pass


def iter_jobs() -> Iterator[Job]:
    for source in INPUT_DIR.rglob("*"):
        if not source.is_file():
            continue
        ext = source.suffix.lower()
        rel = source.relative_to(INPUT_DIR)
        rel_posix = rel.as_posix()

        if rel_posix in KEEP_ORIGINAL_PATHS:
            kind = "native"
            out_ext = ext
        elif ext in RASTER_EXTS:
            kind = "raster"
            out_ext = ".webp"
        elif ext in NATIVE_EXTS:
            kind = "native"
            out_ext = ext
        elif ext in VIDEO_EXTS:
            kind = "video"
            out_ext = ".webm"
        else:
            continue

        destination = (OUTPUT_DIR / rel).with_suffix(out_ext)
        yield Job(
            source=source,
            destination=destination,
            kind=kind,
            key=rel_posix,
        )


def convert_raster(source: Path, temp_output: Path) -> None:
    with Image.open(source) as image:
        icc = image.info.get("icc_profile")
        if image.mode in ("RGBA", "LA", "PA") or (image.mode == "P" and "transparency" in image.info):
            out = image.convert("RGBA")
        else:
            out = image.convert("RGB")
        save_kwargs = {
            "format": "WEBP",
            "quality": WEBP_QUALITY,
            "method": WEBP_METHOD,
        }
        if icc:
            save_kwargs["icc_profile"] = icc
        out.save(temp_output, **save_kwargs)


def copy_native(source: Path, temp_output: Path) -> None:
    shutil.copy2(source, temp_output)


def convert_video(source: Path, temp_output: Path) -> None:
    cmd = [
        FFMPEG,
        "-y",
        "-hide_banner",
        "-loglevel", "error",
        "-i", str(source),
        "-c:v", VIDEO_CODEC,
        "-crf", str(VIDEO_CRF),
        "-pix_fmt", VIDEO_PIX_FMT,
        "-b:v", VIDEO_BITRATE_MODE,
        "-c:a", VIDEO_AUDIO_CODEC,
        "-threads", FFMPEG_THREADS,
        "-f", VIDEO_CONTAINER_FORMAT,
        str(temp_output),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def process_job(
    job: Job,
    signatures: Dict[str, Dict[str, str]],
    manifest_entries: Dict[str, Dict[str, object]],
) -> JobResult:
    ready, source_meta, readiness_reason = wait_for_source_ready(job.source)
    if not ready or source_meta is None:
        return JobResult(status="failed", job=job, reason=readiness_reason)

    expected_signature = signatures[job.kind]
    current_entry = manifest_entries.get(job.key)

    if current_entry:
        manifest_source_meta = current_entry.get("source")
        manifest_signature = current_entry.get("signature")
        if (
            manifest_source_meta == source_meta_to_dict(source_meta)
            and manifest_signature == expected_signature
            and job.destination.exists()
            and not is_stale_output(job.destination, source_meta)
            and validate_output(job.destination, job.kind)
        ):
            return JobResult(status="skipped", job=job, source_meta=source_meta)

    job.destination.parent.mkdir(parents=True, exist_ok=True)

    temp_name: Optional[str] = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=job.destination.parent,
            prefix=f".{job.destination.stem}.",
            suffix=job.destination.suffix,
            delete=False,
        ) as tmp:
            temp_name = tmp.name
        temp_path = Path(temp_name)

        if job.kind == "raster":
            convert_raster(job.source, temp_path)
        elif job.kind == "native":
            copy_native(job.source, temp_path)
        else:
            convert_video(job.source, temp_path)

        latest_meta = get_source_meta(job.source)
        if latest_meta != source_meta:
            return JobResult(
                status="failed",
                job=job,
                reason="source metadata changed during processing; publication canceled",
            )

        if not validate_output(temp_path, job.kind):
            return JobResult(status="failed", job=job, reason="temporary output validation failed")

        os.replace(temp_path, job.destination)

        with manifest_lock:
            manifest_entries[job.key] = {
                "source": source_meta_to_dict(source_meta),
                "signature": expected_signature,
                "output": {
                    "path": str(job.destination.relative_to(PROJECT_ROOT).as_posix()),
                    "kind": job.kind,
                    "size": job.destination.stat().st_size,
                    "mtime_ns": job.destination.stat().st_mtime_ns,
                },
            }
        return JobResult(status="processed", job=job, source_meta=source_meta)
    except subprocess.CalledProcessError as exc:
        reason = (exc.stderr or exc.stdout or str(exc)).strip()
        return JobResult(status="failed", job=job, reason=f"ffmpeg/ffprobe error: {reason}")
    except FileNotFoundError as exc:
        return JobResult(status="failed", job=job, reason=f"required binary missing: {exc}")
    except Exception as exc:
        return JobResult(status="failed", job=job, reason=str(exc))
    finally:
        if temp_name and os.path.exists(temp_name):
            try:
                os.unlink(temp_name)
            except OSError:
                pass


def main() -> int:
    signatures = build_signatures()
    manifest_entries = load_manifest(MANIFEST_PATH)

    counts = {"processed": 0, "skipped": 0, "failed": 0}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        in_flight = set()
        max_in_flight = max(1, MAX_WORKERS * 2)

        for job in iter_jobs():
            while len(in_flight) >= max_in_flight:
                done, in_flight = wait(in_flight, return_when=FIRST_COMPLETED)
                for future in done:
                    result = future.result()
                    counts[result.status] += 1
                    if result.status == "failed":
                        print(
                            f"failed type={result.job.kind} source={result.job.source} "
                            f"destination={result.job.destination} reason={result.reason}"
                        )

            in_flight.add(executor.submit(process_job, job, signatures, manifest_entries))

        if in_flight:
            done, _ = wait(in_flight)
            for future in done:
                result = future.result()
                counts[result.status] += 1
                if result.status == "failed":
                    print(
                        f"failed type={result.job.kind} source={result.job.source} "
                        f"destination={result.job.destination} reason={result.reason}"
                    )

    write_manifest_atomic(MANIFEST_PATH, manifest_entries)

    print(
        "summary "
        f"processed={counts['processed']} "
        f"skipped={counts['skipped']} "
        f"failed={counts['failed']} "
        f"max_workers={MAX_WORKERS}"
    )

    return 1 if counts["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
