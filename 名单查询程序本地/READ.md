# 🛡️ 团支部智能核查系统 (Dazzle Secretary Pro)

> **版本**：v3.3 OCR Agent Workbench  
> **开发者**：Dazzle (Software Engineering, 2025 Cohort)  
> **核心驱动**：Python 3.13 + Streamlit + Ollama (Optional)

---

## 📖 简介 (Introduction)
专为高校班委设计的**轻量级名单核查工具**。
告别“人工数人头”和“眼花缭乱找名字”，只需将群接龙或截图文字一键粘贴，系统即可毫秒级生成未完成名单及催办话术。

### ✨ 核心亮点
* **⚡️ 极速模式 (Turbo Mode)**：默认开启。基于 Dazzle 自研的高速匹配算法，**无需安装任何 AI 环境**，0 延迟，0 报错。
* **💾 自动存档 (Auto-Save)**：内置 JSON 持久化引擎，自动保存班级底册，软件关闭数据不丢失。
* **🧩 Agent 架构 (Agent Architecture)**：将 UI、底册、核查计算、AI 解析拆分为独立模块，后续可继续扩展历史记录、Excel 导入、云端 fallback。
* **🖼️ 截图 OCR (Mac / Windows)**：优先使用 PaddleOCR，Tesseract 作为兜底；上传截图后可直接识别文字并进入核查流程。
* **🧽 姓名纠错 (Name Repair)**：OCR 识别出错时，会用底册做模糊修正，例如“李欣燃 -> 李欣然”。
* **🛡️ 双平台支持**：提供 Windows 独立版 (.exe) 与 Mac 适配方案。
* **🧠 AI 深度解析 (可选)**：针对极度混乱的文本，支持调用本地 Ollama 大模型进行模糊推理。

---

## 🧱 v3.0 项目结构

```text
secretary.py       # Streamlit 主界面，只负责交互与展示
agent.py           # 考勤秘书 Agent，调度极速匹配或 Ollama AI 解析
attendance.py      # 核查计算、完成率、未完成名单和提醒话术
roster.py          # 底册读写、姓名清洗、身份冲突处理
ocr.py             # PaddleOCR / Tesseract 截图 OCR
history.py         # 最近核查记录
class_roster.json  # 班级底册数据
requirements.txt   # Python 依赖
requirements-macos.txt   # Mac OCR 依赖
requirements-windows.txt # Windows OCR 依赖
```

### v3.0 升级重点

* **三类身份底册**：支持党员、团员、群众，自动按“党员 > 团员 > 群众”处理跨组冲突。
* **可验证 Agent 输出**：AI 只负责提取候选姓名，最终核查仍由 `attendance.py` 用底册集合计算，避免模型幻觉直接影响结果。
* **未知姓名提示**：AI 识别到但不在当前核查范围内的姓名会单独展示，便于发现 OCR 错字或底册遗漏。
* **核心逻辑可测试**：名单清洗、极速匹配、核查计算已从 Streamlit 页面拆出，后续可以直接加单元测试。

### Mac OCR 安装

Mac 推荐使用 PaddleOCR；Tesseract 和中文语言包作为兜底：

```bash
brew install tesseract tesseract-lang
pip install -r requirements-macos.txt
```

### Windows OCR 安装

Windows 推荐使用 PaddleOCR；官方 Tesseract OCR 作为兜底：

1. 安装 Windows 版 Tesseract OCR，并确保 `tesseract.exe` 在 PATH 中。
2. 安装 Python 依赖：

```bash
pip install -r requirements-windows.txt
```

两端建议上传 PNG/JPG 截图。识别后文本会自动填入“智能核查”的输入框，并经过底册姓名模糊纠错。

---

## 💻 Windows 用户食用指南

### 1. 安装与启动
本软件为**绿色免安装版 (Portable)**。
1.  下载压缩包并解压到电脑任意位置（推荐 `D盘` 或 `文档` 目录）。
    * ⚠️ **警告**：请勿直接在压缩包内运行，否则无法生成存档文件！
2.  找到 `DazzleSecretaryPro.exe`。
3.  **双击运行**。首次启动需等待 5-10 秒释放资源，随后会自动弹出浏览器界面。

### 2. 快捷方式 (推荐)
为了防止误删数据文件，建议不要移动 EXE 文件，而是创建桌面快捷方式：
* `右键 EXE 文件` -> `发送到` -> `桌面快捷方式`。

---

## 🍎 Mac 用户

由于 macOS 的安全机制，Mac 版请按以下步骤操作：

### 1. 绕过安全锁 (Gatekeeper)
苹果系统默认会拦截未签名的第三方软件。
1.  **不要直接双击打开！**
2.  对着 `DazzleSecretaryMac` 图标点击 **右键 (Right Click)**。
3.  选择 **“打开” (Open)**。
4.  在弹出的警告框中点击 **“仍然打开” (Open Anyway)**。

### 2. 权限修复 (如果打不开)
如果提示“文件已损坏”，请在终端 (Terminal) 输入以下命令并回车：
```bash
xattr -cr /Applications/DazzleSecretaryMac
```
---


# 更新日志
## 🚀 Dazzle Secretary Pro v1.0 全新架构与 AI 智能核查升级  2026.2.28

### ✨ 核心新特性 (New Features)

* **🖥 全新现代化 Web 交互 (Streamlit Pro)**
    * 采用 Streamlit Pro 打造了全新的侧边栏导航与实时数据看板。
    * 实时显示班级基数（团员/群众/总计），以及核查任务的“应到/实到/待冲锋”进度和完成率。
* **🧠 AI 智能核查引擎 (Ollama + Qwen 3.0)**
    * 引入阿里通义千问本地化部署，支持“极速匹配模式”。
    * 支持直接粘贴乱序文本 AI 自动进行秒级核对，零延迟输出未完成与已完成名单。
* **🗂 智能底册管理系统**
    * 录入/更新班级底册面板，支持一行一个名字的快速录入。
    
* **⚡️ 底层性能与硬件优化**
    * 核心语言 **Python 3.13**。



## 🚀 Dazzle Secretary Pro v2.0 全新架构与 AI 智能核查升级  2026.3.20

### ✨ 核心新特性 (New Features)
* ** 功能补全 **
    * 在原有的基础上增加了党员名单的录用和匹配
    * 保持了基本的逻辑和设计方案


## 🚀 Dazzle Secretary Pro v3.0 Agent 架构升级  2026.5.9

### ✨ 核心新特性 (New Features)
* **模块化升级**
    * `secretary.py` 专注 UI 展示。
    * `agent.py` 专注本地 Ollama Agent 调度。
    * `attendance.py` 专注核查计算。
    * `roster.py` 专注底册读写与清洗。
* **核查可信度提升**
    * 极速模式保持本地精确匹配。
    * AI 模式只输出候选姓名，最终由程序和底册做确定性比对。
    * 新增“不在当前核查范围内”的识别结果提示。
* **后续扩展准备**
    * 为 Excel 导入导出、历史记录、多班级底册、云端模型 fallback 留出清晰边界。


## 🚀 Dazzle Secretary Pro v3.3 OCR 识图核查升级  2026.5.10

### ✨ 核心新特性 (New Features)
* **截图识别**
    * 智能核查页新增截图上传和“识别图片文字”按钮。
    * Mac / Windows 均优先使用 PaddleOCR。
    * Tesseract OCR + `pytesseract` 作为兜底引擎。
    * 新增图片预处理：放大、灰度、自动对比度、锐化。
    * 新增 OCR 姓名模糊纠错。
* **核查记录**
    * 每次核查自动保存摘要。
    * 支持查看最近核查结果、快速复制提醒话术。
* **结果导出**
    * 本次核查结果可导出 CSV，包含已完成、未完成和异常姓名。
