from pathlib import Path

def save_file(path: Path, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
