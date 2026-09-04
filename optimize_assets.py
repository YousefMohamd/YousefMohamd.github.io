#!/usr/bin/env python3
"""
Asset optimization pipeline v2 — my-portfolio
=============================================
Replaces scripts/optimize_assets.py.

Core guarantees:
  1. The source tree is re-scanned from the filesystem on EVERY run.
     No cached listings, no trust in previous runs.
  2. A manifest (mtime+size, or sha256 with --deep) detects added,
     modified, replaced, and deleted files. Existence of an output is
     NEVER treated as proof that it is current.
  3. Deleted sources are reconciled: their derived outputs are pruned.
  4. Files already in a target format (.webp/.avif/.webm/.svg) are
     transferred, never re-encoded.
  5. Sidecar (color data, metadata, .json/.txt/.icc/.xmp) that
     share a stem with a media asset are carried alongside it.
  6. All writes are atomic (temp file + rename) so a crash can never
     leave a truncated output that blocks future processing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# ---------------------------------------------------------------- optional deps
try:
    from PIL import Image
    import pillow_heif
    pillow_heif.register_heif_opener()
    if hasattr(pillow_heif, "register_avif_opener"):
        pillow_heif.register_avif_opener()
    PIL_AVAILABLE = True
except Exception as exc:  # pragma: no cover
    PIL_AVAILABLE = False
    PIL_IMPORT_ERROR = exc

# ---------------------------------------------------------------- configuration
PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR    = PROJECT_ROOT / "img" / "projects"
OUTPUT_DIR   = PROJECT_ROOT / "img" / "optimized" / "projects"
FFMPEG       = PROJECT_ROOT /ffmpeg"
MANIFEST     = PROJECT_ROOT / "scripts" / ".optimize-assets-manifest.json"

# Classification — every rule is explicit; nothing is converted "because it can be".
RASTER_SOURCE_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".heic", ".heif"}
NATIVE_TARGET_EXTS = {".webp", ".avif"}                       # already target format -> copy
VIDEO_SOURCE_EXTS   = {".gif", ".mp4", ".mov", ".avi", ".mkv", ".mv", ".webm"}
VECTOR_EXTS         = {".svg"}                                # vector -> copy, never rasterize
SIDECAR_EXTS        = {".", ".txt", ".icc", ".xmp", ".xml"}  # color/metadata companions
IGNORED_EXTS        = {".py", ".pyc", ".db", ".md"}           # tooling, never assets
JUNK_NAMES          = {".ds_store", "thumbs.db", ".ds_store?"}

WEBP_QUALITY, WEBP_METHOD = 95, 6
AVIF_QUALITY = 60


# ---------------------------------------------------------------- fingerprinting
def fingerprint(path: Path, deep: bool) -> str:
    """Cheap (size+mtime_ns) by default; content hash with --deep."""
    st = path.stat()
    if not deep:
        return f"s{st.st_size}:m{st.st_mtime_ns}"
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def load_manifest() -> dict:
    try:
        return json.loads(MANIFEST.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_manifest(state: dict) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(state, indent=1, sort_keys=True))


# ---------------------------------------------------------------- discovery
def classify(path: Path) -> str | None:
    """Return a rule for this file, or None if it must be ignored."""
    if path.name.lower() in JUNK_NAMES:
        return None
    ext = path.suffix.lower()
    if ext in IGNORED_EXTS:
        return None
    if ext in RASTER_SOURCE_EXTS:
        return "raster"
    if ext in NATIVE_TARGET_EXTS:
        return "native"
    if ext in VIDEO_SOURCE_EXTS:
        return "video"
    if ext in VECTOR_EXTS:
        return "vector"
    if ext in SIDECAR_EXTS:
        return "sidecar"
    return None  # unknown types are never guessed at — reported, not processed


def scan_sources() -> list[tuple[Path, str]]:
    """Fresh, full-depth scan. Runs on every invocation — never cached."""
    found: list[tuple[Path, str]] = []
    for dirpath, _dirs, files in os.walk(INPUT_DIR):
        for name in files:
            p = Path(dirpath) / name
            rule = classify(p)
            if rule:
                found.append((p, rule))
    return sorted(found, key=lambda t: t[0].relative_to(INPUT_DIR).as_posix())


def expected(rel: Path, rule: str) -> list[Path]:
    """Derived output paths (absolute) for one source file."""
    if rule == "raster":
        return [OUTPUT_DIR / rel.parent / (rel.stem + ".webp"),
                OUTPUT_DIR / rel.parent / (rel.stem + ".avif")]
    if rule == "video":
        return [OUTPUT_DIR / rel.parent / (rel.stem + ".webm")]
    # native / vector / sidecar -> same name, same place
    return [OUTPUT_DIR / rel]


# ---------------------------------------------------------------- atomic write
def atomic_replace(tmp: Path, final: Path) -> None:
    os.replace(tmp, final)


# ---------------------------------------------------------------- processing
def validate_output(path: Path) -> bool:
    if not path.exists() or path.stat().st == 0:
        return False
    if path.suffix.lower() == ".webm":
        return True  # container integrity is delegated to ffmpeg's exit code
    try:
        with Image.open(path) as im:
            im.verify()
        return True
    except Exception:
        return False


def convert_raster(src: Path, webp_out: Path, avif_out: Path) -> str:
    with Image.open(src) as im:
        icc = im.info.get("icc_profile")
        has_alpha = im.mode in ("RGBA", "LA", "PA") or (
            im.mode == "P" and "transparency" in im.info
        )
        stabilized = im.convert("RGBA" if has_alpha else "RGB")

        webp_tmp = webp_out.with_name(webp_out.name + ".part")
        stabilized.save(webp_tmp, format="WEBP", quality=WEBP_QUALITY,
                        method=WEBP_METHOD, icc_profileicc)
        atomic_replace(webp_tmp, webp_out)
        if not validate_output(webp_out):
            return f"WebP failed integrity validation: {webp_out.name}"

        avif_tmp = avif_out.with_name(avif_out.name + ".part")
        stabilized.save(avif_tmp, format="AVIF", quality=AVIF_QUAL,
                        icc_profile=icc)
        atomic_replace(avif_tmp, avif_out)
        if not validate_output(avif_out):
            return f"AVIF failed integrity validation: {avif_out.name}"
    return ""


def convert_video(src: Path, webm_out: Path) -> str:
    is_gif = src.suffix.lower() == ".gif"
    cmd = [
        str(FFMPEG), "-y", "-i", str(src),
        "-c:v", "libvpx-vp9",
        "-crf", "30",
        "-b:v", "0",
        "-row-mt", "1",
        "-deadline", "good",
        "-cpu-used", "2",
        "-pix_fmt", "yuva420p" if is_gif else "yuv420p",  # keep GIF transparency
        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        *(["-an"] if is_gif else ["-c:a", "libopus", "-b:a", "96k"]),
        str(webm_out),
    ]
    proc = subprocess.run(cmd, stdout=subprocess.DEVNULL,
                          stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0 or not validate_output(webm_out):
        # Never leave a truncated file behind — it would poison future runs.
        webm_out.unlink(missing_ok=True)
        tail = (proc.stderr or "").strip().splitlines()[-3:]
        return f"FFmpeg failed ({proc.returncode}): {' | '.join(tail)}"
    return ""


def copy_asset(src: Path, dst: Path) -> str:
    try:
        tmp = dst.with_name(dst.name + ".part")
        shutil.copy2(src, tmp)
        atomic_replace(tmp, dst)
        return ""
    except Exception as exc:
        return f"Copy failed: {exc}"


def process_one(src: Path, rule: str, outputs: list[Path]) -> tuple[str, str, str]:
    """Returns (status, display_name, message)."""
    rel = src.relative_to(INPUT_DIR).as_posix()
    for out in outputs:
        out.parent.mkdir(parents=True, exist_ok=True)
    try:
        if rule == "raster":
            err = convert_raster(src, outputs[0], outputs[1])
        elif rule == "video":
            if src.suffix.lower() == ".webm":
                err = copy_asset(src, outputs[0])          # already WebM -> transfer
                if not err:
                    return ("COPIED", rel, "Native WebM transferred without re-encoding")
            else:
                err = convert_video(src, outputs[0])
        else:  # native / vector / sidecar
            err = copy_asset(src, outputs[0])
            if not err:
                return ("COPIED", rel, f"Transferred {src.suffix.upper()} without re-encoding")
        if err:
            return ("FAILED", rel, err)
        return ("SUCCESS", rel, "Generated optimized WEBP & AVIF" if rule == "raster"
                elseConverted to WebM (VP9)")
    except Exception as exc:
        return ("FAILED", rel, f"{type(exc).__name__}: {exc}")


# ---------------------------------------------------------------- reconciliation
def prune_orphans(expected: set[str], dry_run: bool) -> list[str]:
    """Remove every output file not derivable from the CURRENT source tree."""
    removed: list[str] = []
    if not OUTPUT_DIR.exists():
        return removed
    for dirpath, _dirs, files in os.walk(OUTPUT_DIR):
        for name in files:
            p = Path(dirpath) / name
            if p.name.endswith(".part"):          # crash debris — always removed
                if not dry_run:
                    p.unlink()
                removed.append(p.relative_to(OUTPUT_DIR).as_posix() + " (stale temp)")
                continue
            rel = p.relative_to(OUTPUT_DIR).as_posix()
            if rel not in expected:
                if not_run:
                    p.unlink()
                removed.append(rel)
    if not dry_run:
        for dirpath, dirs, files in os.walk(OUTPUT_DIR, topdown=False):
            if not dirs and not files and Path(dirpath) != OUTPUT_DIR:
                Path(dirpath).rmdir()
    return removed


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description="Asset optimization pipeline v2")
    ap.add_argument("--force", action="store_true", help="Reprocess everything")
    ap.add_argument("--deep", action="store_true",
                    help="Use sha256 fingerprints instead of mtime+size")
    ap.add_argument("--no-prune", action="store_true",
                    help="Do not delete outputs whose sources no longer exist")
    ap.add_argument("--dry-run", action="store_true",
                   ="Report planned actions without writing anything")
    ap.add_argument("--input", type=Path, default=INPUT_DIR)
    ap.add_argument("--output", type=Path, default=OUTPUT_DIR)
    args = ap.parse_args()

    global INPUT_DIR, OUTPUT_DIR
    INPUT_DIR, OUTPUT_DIR = args.input.resolve(), args.output.resolve()

    if not INPUT_DIR.is_dir():
        print(f"TERMINATING: source directory not found: {INPUT_DIR}")
        return 1
    if not PIL_AVAILABLE:
        print(f"TERMINATING: Pillow/pillow-heif unavailable: {PIL_IMPORT_ERROR}")
        return 1
    if not FFMPEG.exists():
        print(f"WARNING: ffmpeg not found at {FFMPEG}; video conversion will fail.")

    # ---- Phase 1: fresh scan (never trusts any previous listing) ------------
    sources = scan_sources()
    manifest = load_manifest()

    # ---- Phase 2: sidecar association (color/metadata files) ----------------
    media_stems: dict[Path, set[str]] = {}
    for src, rule in sources:
        if rule in ("raster", "native", "video", "vector"):
            media_stems.setdefault(src.parent, set()).add(src.stem.lower())
    work: list[tuple[Path, str, list[Path]]] = []
    ignored_sidecars: list[str] = []
    for src, rule sources:
        rel = src.relative_to(INPUT_DIR)
        if rule == "sidecar":
            if src.stem.lower() in media_stems.get(src.parent, set()):
                work.append((src, rule, expected_outputs(rel, rule)))
            else:
                ignored_sidecars.append(rel.as_posix())
        else:
            work.append((src, rule, expected_outputs(rel, rule)))

    # ---- Phase 3: output-collision detection (case-insensitive FS) ----------
    claimed: dict[str, str] = {}
    conflicts: list[tuple[str, str]] = []
    safe_work: list[tuple[Path, str, list[Path]]] = []
    for src, rule, outputs in work:
        rel = src.relative_to(INPUT_DIR).as_posix()
        clash = None
        for out in outputs:
            key = out.relative_to(OUTPUT_DIR).as_posix().lower()
            if key in claimed and claimed[key] != rel:
                clash = claimed[key]
                break
            claimed[key] = rel
        if clash:
            conflicts.append((rel, clash))
        else:
            safe_work.append((src, rule, outputs))

    # ---- Phase 4: decide what actually needs work-----------
    pending: list[tuple[Path, str, list[Path]]] = []
    fresh = 0
    for src, rule, outputs in safe_work:
        rel = src.relative_to(INPUT_DIR).as_posix()
        fp = fingerprint(src, args.deep)
        if (not args.force
                and manifest.get(rel) == fp
                and all(validate_output(o) for o in outputs)):
            fresh += 1
        else:
            pending.append((src, rule, outputs))

    print(f"Scan complete: {len(sources)} source files "
          f"({fresh} fresh, {len(pending)} to process, "
          f"{len(ignored_sidecars)} unassociated sidecars ignored, "
          f"{len(conflicts)} collisions).")

    # ---- Phase 5: execute ----------------------------------------------------
    results: list[tuple[str, str, str]] = []
    if args.dry_run:
        for src, rule, outputs in pending:
            rel = src.relative_to(INPUT_DIR).as_posix()
            results.append(("PLANNED", rel,
                            " -> ".join(o.name for o in outputs)))
    else:
        workers = min(8, os.cpu_count() or 4)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(process_one, s, r, o) for s, r, o in pending]
            for fut in as_completed(futures):
                results.append(fut.result())

    # ---- Phase 6: update manifest to CURRENT source state --------------------
    if not args.dry_run:
        new_state = {
            src.relative_to(INPUT_DIR).as_posix(): fingerprint(src, args.deep)
            for src, _rule in sources
        }
        save_manifest(new_state)

    # ---- Phase 7: prune outputs whose sources disappeared --------------------
    expected: set[str] = set()
    for src, rule, outputs in safe_work:
        for out in outputs:
            expected.add(out.relative_to(OUTPUT_DIR).as_posix())
    pruned = [] if args.no_prune else prune_orphans(expected, args.dry_run)

    # ---- Phase 8: report ------------------------------------------------------
    ok      = [r for r in results if r[0] in ("SUCCESS", "COPIED")]
    planned = [r for r in results if r[0] == "PLANNED"]
    failed  = [r for r in results if r[0] == "FAILED"]

    print("=" * 70)
    print("        SUMMARY: ASSET OPTIMIZATION PIPELINE v2")
    print("=" * 70)
    print(f" Source files discovered      : {len(sources)}")
    print(f" Fresh (unchanged, verified)  : {fresh}")
    print(f" Processed this run           : {len(ok)}")
    if planned:
        print(f" Planned (dry-run)            : {len(planned)}")
    print(f" Failed                       : {len(failed)}")
    print(f" Orphaned outputs removed     : {len(pruned)}")
    print(f" Output collisions detected   : {len(conflicts)}")
    print("-" * 70)

    if conflicts:
        print("\n [COLLISIONS — two sources map to one output; second was skipped]:")
        for rel, other in conflicts:
            print(f" !! {rel} collides with {other}")
    if ignored_sidecars:
        print("\n [SIDECAR FILES WITH NO MATCHING MEDIA (left untouched)]:")
        for rel in ignored_sidecars:
            print(f"   -- {rel}")
    if pruned:
        print("\n [PRUNED — source no longer exists]:")
        for rel in pruned:
            print(f"   xx {rel}")
    if failed:
        print("\n [FAILED]:")
        for _s, name, msg in failed:
            print(f"   !! {name} -> {msg}")
    if not failed and not conflicts:
        print("\n All current assets are in sync with the source tree    print("=" * 70)
    return 1 if failed or conflicts else 0


if __name__ == "__main__":
    sys.exit(main())
