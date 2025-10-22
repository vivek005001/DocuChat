import pdfminer.high_level
import os

def extract_text(file_path: str, mime_type: str):
    if mime_type == "application/pdf":
        return pdfminer.high_level.extract_text(file_path)
    elif mime_type == "text/plain":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError("Unsupported file type")
