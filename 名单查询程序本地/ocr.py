import platform
from pathlib import Path
import shutil

from PIL import Image


def available_ocr_engines():
    system = platform.system()
    engines = []

    if system == "Darwin":
        if _has_tesseract():
            engines.append("Mac Tesseract")
        return engines

    if system == "Windows":
        if _has_tesseract():
            engines.append("Windows Tesseract")
        return engines

    return engines


def ocr_platform_name():
    system = platform.system()
    if system == "Darwin":
        return "Mac"
    if system == "Windows":
        return "Windows"
    return system or "Unknown"


def ocr_setup_hint():
    system = platform.system()
    if system == "Darwin":
        return "Mac OCR 需要 brew install tesseract tesseract-lang，并 pip install pytesseract。"
    if system == "Windows":
        return "Windows OCR 需要安装 Tesseract OCR 桌面程序，并 pip install pytesseract。"
    return "当前系统未配置 OCR 方案；本项目只提供 Mac 和 Windows OCR 路线。"


def ocr_status_message():
    engines = available_ocr_engines()
    if engines:
        return f"{ocr_platform_name()} OCR：已就绪（{' / '.join(engines)}）"
    return f"{ocr_platform_name()} OCR：未就绪。{ocr_setup_hint()}"


def extract_text_from_image(image_bytes, filename="uploaded.png"):
    system = platform.system()
    engines = available_ocr_engines()

    if system == "Darwin":
        if "Mac Tesseract" not in engines:
            raise RuntimeError(ocr_status_message())
        return _extract_with_tesseract(image_bytes)

    if system == "Windows":
        if "Windows Tesseract" not in engines:
            raise RuntimeError(ocr_status_message())
        return _extract_with_tesseract(image_bytes)

    raise RuntimeError(ocr_status_message())


def _has_tesseract():
    try:
        __import__("pytesseract")
    except Exception:
        return False
    return _tesseract_cmd() is not None


def _tesseract_cmd():
    found = shutil.which("tesseract")
    if found:
        return found

    candidates = [
        "/opt/homebrew/bin/tesseract",
        "/usr/local/bin/tesseract",
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    return None


def _extract_with_tesseract(image_bytes):
    from io import BytesIO
    import pytesseract

    tesseract_cmd = _tesseract_cmd()
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    image = Image.open(BytesIO(image_bytes))
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")

    try:
        return pytesseract.image_to_string(image, lang="chi_sim+eng").strip()
    except Exception:
        return pytesseract.image_to_string(image).strip()
