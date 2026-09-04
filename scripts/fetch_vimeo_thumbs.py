from __future__ import annotations

import json
import os
import re
import ssl
import urllib.request
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_DIR = PROJECT_ROOT / "projects"
OUTPUT_DIR = PROJECT_ROOT / "img" / "optimized" / "projects" / "short-film"
MANIFEST_PATH = PROJECT_ROOT / "node_modules" / ".cache" / "vimeo-thumbs-manifest.json"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

UNVERIFIED_CONTEXT = ssl._create_unverified_context()
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"


def open_url(url: str, timeout: int = 20):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    return urllib.request.urlopen(req, timeout=timeout, context=UNVERIFIED_CONTEXT)


def extract_vimeo_id(content: str) -> str | None:
    match = re.search(r'vimeoId:\s*(\d+)', content)
    return match.group(1) if match else None


def fetch_vimeo_thumbnail(vimeo_id: str) -> str | None:
    oembed_url = (
        f"https://vimeo.com/api/oembed.json?url=https://vimeo.com/{vimeo_id}"
        "&width=1280&height=720"
    )
    try:
        with open_url(oembed_url, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        thumb = data.get("thumbnail_url")
        if not thumb:
            return None
        # استخدام الرابط الأصلي كما قدمه Vimeo
        return thumb
    except Exception as exc:
        print(f"Failed to fetch oEmbed for {vimeo_id}: {exc}")
        return None


def load_manifest(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, OSError):
        return {}


def save_manifest(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    with temp.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
    os.replace(temp, path)


def convert_to_webp(source_bytes: bytes, destination: Path) -> bool:
    try:
        from PIL import ImageEnhance

        tmp = destination.with_suffix(".src")
        tmp.write_bytes(source_bytes)
        with Image.open(tmp) as img:
            img = img.convert("RGB")

            # الأبعاد المستهدفة 16:9
            target_w, target_h = 1280, 720
            w, h = img.size
            aspect_target = target_w / target_h
            aspect_src = w / h

            # قص مركزي إلى نسبة 16:9
            if aspect_src > aspect_target:
                new_w = int(h * aspect_target)
                x = (w - new_w) // 2
                img = img.crop((x, 0, x + new_w, h))
            elif aspect_src < aspect_target:
                new_h = int(w / aspect_target)
                y = (h - new_h) // 2
                img = img.crop((0, y, w, y + new_h))

            # تكبير/تصغير إلى 1280x720
            img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)

            # تحسين حدة خفيف
            sharpener = ImageEnhance.Sharpness(img)
            img = sharpener.enhance(1.2)

            img.save(destination, "WEBP", quality=90, method=6)

        tmp.unlink(missing_ok=True)
        return True
    except Exception as exc:
        print(f"Error converting to WebP: {exc}")
        return False


def main() -> int:
    manifest = load_manifest(MANIFEST_PATH)
    updated = False

    for md_file in PROJECTS_DIR.glob("short-film-*.md"):
        content = md_file.read_text(encoding="utf-8")
        vimeo_id = extract_vimeo_id(content)
        if not vimeo_id:
            continue

        output = OUTPUT_DIR / f"{vimeo_id}.webp"

        if manifest.get(vimeo_id) == vimeo_id and output.exists() and output.stat().st_size > 0:
            continue

        thumb_url = fetch_vimeo_thumbnail(vimeo_id)
        if not thumb_url:
            continue

        try:
            with open_url(thumb_url, timeout=30) as resp:
                source_bytes = resp.read()
        except Exception as exc:
            print(f"Failed to download thumbnail for {vimeo_id}: {exc}")
            continue

        if convert_to_webp(source_bytes, output):
            manifest[vimeo_id] = vimeo_id
            updated = True
            print(f"Saved WebP: {output.relative_to(PROJECT_ROOT)}")
        else:
            print(f"Conversion failed for {vimeo_id}")

    if updated:
        save_manifest(MANIFEST_PATH, manifest)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
