"""One explicit download from the public model repository. Never used during inference."""
from pathlib import Path
import hashlib
import json
import shutil
import urllib.request

ROOT = Path(__file__).resolve().parent
REPO = "sentence-transformers/all-MiniLM-L6-v2"
REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
FILES = {"tokenizer.json": "tokenizer.json", "onnx/model.onnx": "model.onnx", "config.json": "config.json"}

def main():
    target = ROOT / "models"
    target.mkdir(exist_ok=True)
    records = []
    for remote, local in FILES.items():
        path = target / local
        url = f"https://huggingface.co/{REPO}/resolve/{REVISION}/{remote}"
        if not path.exists():
            print(f"Downloading {remote} from the public pinned revision", flush=True)
            part = target / (local + ".part")
            # A denied or failed response raises immediately. No mirror, auth or retry loop.
            with urllib.request.urlopen(url, timeout=45) as response, part.open("wb") as stream:
                shutil.copyfileobj(response, stream)
            part.replace(path)
        records.append({"file": local, "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "url": url})
    manifest = {"repository": REPO, "revision": REVISION, "license": "Apache-2.0", "files": records}
    (target / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2), flush=True)

if __name__ == "__main__":
    main()
