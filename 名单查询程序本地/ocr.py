import platform
from pathlib import Path
import tempfile
import shutil

from PIL import Image, ImageFilter, ImageOps


def available_ocr_engines():
    engines = []

    if _has_paddleocr():
        engines.append("PaddleOCR")

    system = platform.system()
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
        return "推荐安装 PaddleOCR；兜底方案需要 brew install tesseract tesseract-lang，并 pip install pytesseract。"
    if system == "Windows":
        return "推荐安装 PaddleOCR；兜底方案需要安装 Tesseract OCR 桌面程序，并 pip install pytesseract。"
    return "当前系统未配置 OCR 方案；本项目只提供 Mac 和 Windows OCR 路线。"


def ocr_status_message():
    engines = available_ocr_engines()
    if engines:
        return f"{ocr_platform_name()} OCR：已就绪（{' / '.join(engines)}）"
    return f"{ocr_platform_name()} OCR：未就绪。{ocr_setup_hint()}"


def extract_text_from_image(image_bytes, filename="uploaded.png"):
    system = platform.system()
    engines = available_ocr_engines()

    texts = []
    if "PaddleOCR" in engines:
        try:
            texts.append(_extract_with_paddleocr(image_bytes))
        except Exception:
            pass

    if system == "Darwin":
        if "Mac Tesseract" not in engines:
            if texts:
                return _merge_texts(texts)
            raise RuntimeError(ocr_status_message())
        texts.append(_extract_with_tesseract(image_bytes))
        return _merge_texts(texts)

    if system == "Windows":
        if "Windows Tesseract" not in engines:
            if texts:
                return _merge_texts(texts)
            raise RuntimeError(ocr_status_message())
        texts.append(_extract_with_tesseract(image_bytes))
        return _merge_texts(texts)

    raise RuntimeError(ocr_status_message())


def _merge_texts(texts):
    lines = []
    for text in texts:
        for line in str(text or "").splitlines():
            clean = line.strip()
            if clean:
                lines.append(clean)
    return "\n".join(dict.fromkeys(lines)).strip()


def _has_paddleocr():
    try:
        __import__("paddleocr")
        __import__("paddle")
    except Exception:
        return False
    return True


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

    image = _preprocess_image(Image.open(BytesIO(image_bytes)))

    try:
        return pytesseract.image_to_string(image, lang="chi_sim+eng", config="--psm 6").strip()
    except Exception:
        return pytesseract.image_to_string(image, config="--psm 6").strip()


def _extract_with_paddleocr(image_bytes):
    from io import BytesIO
    from paddleocr import PaddleOCR

    image = _preprocess_image(Image.open(BytesIO(image_bytes)))
    with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as tmp:
        image.save(tmp.name)
        tmp.flush()

        ocr = _make_paddle_ocr()
        try:
            result = ocr.ocr(tmp.name, cls=True)
        except TypeError:
            result = ocr.ocr(tmp.name)
        except AttributeError:
            result = ocr.predict(tmp.name)

    lines = _flatten_paddle_result(result)
    return "\n".join(lines).strip()


def _make_paddle_ocr():
    from paddleocr import PaddleOCR

    for kwargs in (
        {"use_angle_cls": True, "lang": "ch", "show_log": False},
        {"use_angle_cls": True, "lang": "ch"},
        {"lang": "ch"},
    ):
        try:
            return PaddleOCR(**kwargs)
        except Exception:
            continue
    return PaddleOCR()


def _flatten_paddle_result(result):
    lines = []

    def visit(node):
        if node is None:
            return
        if isinstance(node, dict):
            for key in ("rec_texts", "texts"):
                values = node.get(key)
                if isinstance(values, list):
                    lines.extend(str(v) for v in values if str(v).strip())
                    return
            for value in node.values():
                visit(value)
            return
        if isinstance(node, (list, tuple)):
            if len(node) >= 2 and isinstance(node[1], (list, tuple)) and node[1]:
                text = node[1][0]
                if isinstance(text, str):
                    lines.append(text)
                    return
            for item in node:
                visit(item)

    visit(result)
    return list(dict.fromkeys(line.strip() for line in lines if line.strip()))


def _preprocess_image(image):
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")
    image = ImageOps.exif_transpose(image)

    width, height = image.size
    scale = 2
    if max(width, height) < 1200:
        scale = 3
    if scale > 1:
        image = image.resize((width * scale, height * scale), Image.Resampling.LANCZOS)

    gray = ImageOps.grayscale(image)
    gray = ImageOps.autocontrast(gray)
    gray = gray.filter(ImageFilter.SHARPEN)
    return gray
