# Dazzle Secretary Pro

本项目是一个基于 Streamlit 和本地 Ollama 模型的团支部名单核查工具，用于从群接龙、OCR 文本或 Excel 粘贴内容中识别已完成人员，并生成未完成提醒。

## 当前能力

- 底册持久化：班级名单存储在 `class_roster.json`，年级名单存储在 `grade_roster.json`
- 身份模式：班团支书使用单班底册，年团支书维护年级底册和多个分班底册
- 身份优先级清洗：党员 > 团员 > 群众
- 极速匹配：直接用底册姓名匹配输入文本
- AI 解析：通过 Ollama 从乱序文本中提取姓名
- 截图 OCR：优先 PaddleOCR，Tesseract 作为 Mac/Windows 兜底
- 高精度 OCR：PaddleOCR 进程内缓存，识别时显示阶段进度条
- OCR 纠错：对疑似 OCR 错字姓名进行底册模糊修正
- 核查结果：展示应到、实到、未到、完成率和群提醒话术

## 升级后的结构

```text
secretary.py      # Streamlit UI
roster.py         # 底册读写、姓名清洗、核查范围选择
attendance.py     # 核查计算、结果结构、提醒文案
agent.py          # Ollama 考勤秘书 Agent
ocr.py            # PaddleOCR / Tesseract 截图 OCR
class_roster.json # 班团支书单班底册
grade_roster.json # 年团支书年级底册
```

## 身份和年级底册

侧边栏可以选择两种身份：

- 班团支书：保持单班核查流程，以当前班级底册为主。
- 年团支书：以年级为主视角，可选择“全年级”核查，也可维护多个分班底册作为年级数据分组。

两种身份的名单互相独立。班团支书保存时只写入 `class_roster.json`；年团支书保存、添加或删除分组时只写入 `grade_roster.json`。年团支书完成一次核查后，会额外展示全年级汇总对比表，按分班底册列出应核查、已完成、未完成和完成率。

## 运行方式

```bash
streamlit run secretary.py
```

如果要使用 AI 深度解析，请先确认 Ollama 已启动，并且本地有可用模型，例如 `qwen3:8b`。

## macOS 应用打包

本项目提供轻量 macOS 应用打包脚本：

```bash
./build_macos_app.sh
```

构建产物位于 `dist-macos/`：

- `Dazzle Secretary.app`：macOS 应用包
- `Dazzle-Secretary-macOS.zip`：适合放到网站下载的压缩包
- `Dazzle-Secretary-macOS.dmg`：可选的 macOS 下载镜像

当前应用包采用首启安装依赖的方式：第一次打开会在用户目录 `~/Library/Application Support/Dazzle Secretary` 创建独立 Python 环境并安装依赖，之后再启动会直接复用该环境。由于应用未做 Apple Developer ID 签名和公证，用户首次打开时可能需要在系统设置中允许打开。

## OCR 截图识别

### Mac

Mac 推荐使用 PaddleOCR；Tesseract 作为兜底：

```bash
brew install tesseract tesseract-lang
pip install -r requirements-macos.txt
```

### Windows

Windows 推荐使用 PaddleOCR；Tesseract 作为兜底：

1. 安装 Windows 版 Tesseract OCR。
2. 安装 Python 依赖：

```bash
pip install -r requirements-windows.txt
```

两端都推荐上传 PNG/JPG 截图。识别后文本会自动进入核查文本框；系统会再用底册做姓名模糊纠错。

高精度 OCR 开关打开后会使用 PaddleOCR。首次识别需要初始化模型，后续同一轮 Streamlit 进程会复用已加载模型，避免每次点击都重新启动 PaddleOCR。界面会显示“准备图片 / 初始化模型 / 正在识别 / 整理结果”的进度条；如果 PaddleOCR 未返回文本，系统再切换到 Tesseract 兜底。

## 后续可升级方向

- 增加 Excel 导入/导出
- 增加相似姓名提示，例如 OCR 错字、数字夹杂、人名缺字
- 增加可复制的不同语气催办话术
