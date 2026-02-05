import sys
import os
import requests
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6 import uic

class MySpider(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 1. 动态获取 UI 文件路径
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # 注意：这里的文件名必须和你保存的一模一样
        ui_file_path = os.path.join(base_dir, "爬虫ui设计.ui") 

        # 2. 加载界面
        try:
            uic.loadUi(ui_file_path, self)
        except FileNotFoundError:
            QMessageBox.critical(self, "错误", f"找不到UI文件: {ui_file_path}")
            sys.exit(1)

        # 3. 连接按钮
        # 你的界面里按钮叫 pushButton
        self.pushButton.clicked.connect(self.start_crawling)

    def start_crawling(self):
        # --- 获取界面数据 ---
        
        # 1. 获取网址 (界面里叫 lineEdit)
        url = self.lineEdit.text().strip()
        
        # 2. 获取请求方式 (界面里叫 combo_method，这个对上了)
        try:
            method = self.combo_method.currentText()
        except:
            method = "get" # 容错
            
        # 3. 获取POST参数 (界面里叫 data_input，这个也对上了)
        try:
            raw_data = self.data_input.text().strip()
        except:
            raw_data = ""

        # 4. 校验
        if not url:
            QMessageBox.warning(self, "提醒", "网址不能为空！")
            return

        # --- 界面反馈 ---
        # 界面里的大白板叫 textEdit
        self.textEdit.setText(f"🚀 正在发起 {method} 请求: {url} ...")
        QApplication.processEvents() # 强制刷新

        # --- 爬虫逻辑 ---
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = None

            if method == "get":
                response = requests.get(url, headers=headers, timeout=5)
            
            elif method == "post":
                # 处理 JSON 数据
                payload = {}
                if raw_data:
                    try:
                        payload = json.loads(raw_data)
                    except:
                        self.textEdit.setText("❌ JSON 格式错误！请检查你的参数。")
                        return
                response = requests.post(url, headers=headers, json=payload, timeout=5)

            # --- 显示结果 ---
            response.encoding = 'utf-8'
            preview = response.text[:10000] # 只显示前10000字
            
            msg = f"✅ 成功响应[{method}] 状态码: {response.status_code}\n\n{preview}..."
            self.textEdit.setText(msg)

        except Exception as e:
            self.textEdit.setText(f"😭 请求失败:\n{str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MySpider()
    window.show()
    sys.exit(app.exec())
