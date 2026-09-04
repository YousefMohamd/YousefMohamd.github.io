import os
from pathlib import Path
print("=== PYTHON PATH RESOLUTION ===")
p_resolve = Path(__file__).resolve().parents[1] / "img" / "optimized" / "projects" / "concept-art"
print(f"[Python .resolve()] Target: {p_resolve}\n[Python .resolve()] Exists: {p_resolve.exists()}")

p_abspath = Path(os.path.abspath(__file__)).parent.parent / "img" / "optimized" / "projects" / "concept-art"
print(f"[Python abspath()]  Target: {p_abspath}\n[Python abspath()]  Exists: {p_abspath.exists()}")
