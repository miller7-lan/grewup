🕸️ DazzleSpider - 可视化爬虫请求工具
DazzleSpider 是一款为大一软件工程实践打造的轻量级桌面端爬虫工具。它将复杂的 HTTP 请求过程封装在直观的 GUI 界面中，支持开发者及非技术人员快速进行接口测试与数据采集。

✨ 核心特性
双模式请求：完美支持 GET 获取数据与 POST 提交负载。

可视化操作：基于 PyQt6 打造，告别黑框框，实时显示响应源码。

跨平台交付：提供 Windows (.exe) 与 macOS (.app) 双端支持，环境零依赖。

工程化隔离：采用虚拟环境管理依赖，确保代码的高可移植性。

🛠️ 技术栈
语言：Python 3.12

界面库：PyQt6 (Qt Designer)

网络库：Requests

打包工具：PyInstaller


对于开发者
如果你想在本地调试代码：

克隆仓库：git clone https://github.com/你的用户名/DazzleSpider.git

安装依赖：pip install requests PyQt6

运行：python spider.py

📂 项目结构
Plaintext
项目一：爬虫小程序/
├── 爬虫ui设计.ui          # Qt Designer 设计的界面文件
├── Qt设计.py             # 核心逻辑与事件处理 
└── README.md            # 你正在看的这份说明


🎓 开发日志
本项目作为河南大学软件工程专业大一第一学期的实战练习，旨在打通从需求分析、界面设计、功能实现到最终打包交付的完整软件开发链路。