import os
from PIL import Image
import pillow_heif
from concurrent.futures import ThreadPoolExecutor

pillow_heif.register_heif_opener()

INPUT_DIR = "img"
OUTPUT_DIR = "img/optimized"
SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".webp")
WEBP_QUALITY = 82
AVIF_QUALITY = 50

os.makedirs(OUTPUT_DIR, exist_ok=True)


def optimize_image(file_path, root_dir, output_dir):
    try:
        with Image.open(file_path) as img:
            if img.mode == "P":
                img = img.convert("RGBA" if "transparency" in img.info else "RGB")

            relative_path = os.path.relpath(root_dir, INPUT_DIR)
            target_dir = os.path.normpath(os.path.join(output_dir, relative_path))
            os.makedirs(target_dir, exist_ok=True)

            base_name = os.path.splitext(os.path.basename(file_path))[0]

            webp_path = os.path.join(target_dir, f"{base_name}.webp")
            img.save(webp_path, "WEBP", quality=WEBP_QUALITY, method=6)

            try:
                avif_path = os.path.join(target_dir, f"{base_name}.avif")
                img.save(avif_path, "AVIF", quality=AVIF_QUALITY)
            except Exception:
                pass
    except Exception:
        pass


def batch_optimize_images(input_dir, output_dir):
    tasks = []
    with ThreadPoolExecutor() as executor:
        for root, _, files in os.walk(input_dir):
            if "optimized" in root:
                continue
            for file in files:
                if file.lower().endswith(SUPPORTED_FORMATS):
                    file_path = os.path.join(root, file)
                    tasks.append(executor.submit(optimize_image, file_path, root, output_dir))

    for task in tasks:
        task.result()


if __name__ == "__main__":
    batch_optimize_images(INPUT_DIR, OUTPUT_DIR)
