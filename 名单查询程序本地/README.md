# Dazzle Secretary Pro

本项目是一个基于 Streamlit 和本地 Ollama 模型的团支部名单核查工具，用于从群接龙、OCR 文本或 Excel 粘贴内容中识别已完成人员，并生成未完成提醒。

## 当前能力

- 底册持久化：名单存储在 `class_roster.json`
- 身份优先级清洗：党员 > 团员 > 群众
- 极速匹配：直接用底册姓名匹配输入文本
- AI 解析：通过 Ollama 从乱序文本中提取姓名
- 截图 OCR：Mac 和 Windows 分别使用本机 Tesseract OCR
- 核查结果：展示应到、实到、未到、完成率和群提醒话术

## 升级后的结构

```text
secretary.py      # Streamlit UI
roster.py         # 底册读写、姓名清洗、核查范围选择
attendance.py     # 核查计算、结果结构、提醒文案
agent.py          # Ollama 考勤秘书 Agent
ocr.py            # Mac / Windows 截图 OCR
class_roster.json # 班级底册
```

## 运行方式

```bash
streamlit run secretary.py
```

如果要使用 AI 深度解析，请先确认 Ollama 已启动，并且本地有可用模型，例如 `qwen3:8b`。

## OCR 截图识别

### Mac

Mac 版本使用 Homebrew 安装的 Tesseract：

```bash
brew install tesseract tesseract-lang
pip install -r requirements-macos.txt
```

### Windows

Windows 版本使用官方 Tesseract OCR：

1. 安装 Windows 版 Tesseract OCR。
2. 安装 Python 依赖：

```bash
pip install -r requirements-windows.txt
```

两端都推荐上传 PNG/JPG 截图。识别后文本会自动进入核查文本框。

## 后续可升级方向

- 增加核查历史记录
- 增加 Excel 导入/导出
- 增加相似姓名提示，例如 OCR 错字、数字夹杂、人名缺字
- 增加多班级底册
- 增加可复制的不同语气催办话术
