import mimetypes
import os

def media_type_of_path(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in [".jpg",".jpeg",".png",".bmp",".webp"]:
        return "image"
    if ext in [".mp3",".wav",".flac",".ogg"]:
        return "audio"
    if ext in [".txt",".json",".csv",".md"]:
        return "text"
    mt, _ = mimetypes.guess_type(path)
    if mt:
        if mt.startswith("image"):
            return "image"
        if mt.startswith("audio"):
            return "audio"
        if mt.startswith("text"):
            return "text"
    return "unknown"

def load_text_from_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()
