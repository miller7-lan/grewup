🛡️ Dazzle-Secretary Pro
2025 级软件工程 7 班团支部自动化核查系统

📖 项目简介
本项目由 河南大学 2025 级软件工程 7 班团支书陈子炫 (Dazzle) 开发。旨在利用人工智能技术解决班级日常事务中繁琐的名单比对工作，如“青年大学习”完成情况核对、团费收缴统计等。

通过集成 本地大语言模型 (Local LLM)，本程序能够自动从杂乱的群聊接龙、截图 OCR 文字中精准提取姓名，并与班级基准数据库进行实时比对。

✨ 核心特性
智能语义提取：基于 dazzle-secretary 专属模型或 qwen2.5:1.5b，自动识别带序号、表情、后缀的非结构化名单。

隐私安全保障：所有 AI 推理流程均在本地 M4 芯片 上完成，确保同学个人信息不上传云端，完全私密安全。

双模式一键核查：预设“全体同学 (48人)”与“团员专项 (32人)”两套名单逻辑，支持一键切换。

极致性能响应：针对 Apple Silicon M4 进行优化，结合 @st.cache_data 技术，实现毫秒级比对反馈。

交互式可视化：未完成名单与匹配成功名单采用统一的 JSON 索引视图，左右对称，清晰直观。

🛠️ 技术栈
核心语言: Python 3.13

前端框架: Streamlit (Responsive UI)

AI 引擎: Ollama (Running dazzle-secretary / qwen2.5)

运行环境: macOS 16 + Apple M4 Silicon

🚀 部署与运行
1. 环境准备
确保本地已安装 Ollama 并拉取轻量化模型以获得最佳速度：

Bash
ollama pull qwen2.5:1.5b
2. 启动程序
在项目根目录下运行：

Bash
streamlit run dazzle_secretary_v3.py
3. 原生 App 封装
本项目已通过 macOS Automator (自动操作) 封装为原生 .app。

支持 Headless 模式启动，无需开启终端窗口。

点击 Launchpad 中的图标即可直接弹出核查界面。

👨‍💻 关于作者
作者: 小炫 (Dazzle / 陈子炫)

身份: 河南大学 2025 级软件工程 7 班团支书

MBTI: ENFJ (主人公)

目标: 致力于 AI 与软件工程的交叉应用

<center>© 2026 Dazzle Silicon Power. Powered by M4 MacBook Air.</center>