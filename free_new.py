import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
from threading import Thread

# 配置
login_url = "http://10.0.0.55/srun_portal_pc?ac_id=8&srun_wait=1&theme=bit"
exit_flag_file = 'exit_flag.txt'

# 设置日志记录配置
logging.basicConfig(
    filename='login_script.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("脚本运行状态")
        self.geometry("400x300")

        # 创建状态显示区
        self.status_text = tk.Text(self, height=15, width=50)
        self.status_text.pack(pady=10)

        # 添加滚动条
        self.scrollbar = tk.Scrollbar(self)
        self.status_text.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.status_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 创建开始按钮
        self.start_button = tk.Button(self, text="开始", command=self.run_script)
        self.start_button.pack(pady=10)

        # 初始化状态变量
        self.username = None
        self.password = None
        self.sleep_time = None

    def log_message(self, message):
        # 使用 after 方法确保在主线程中更新 GUI
        self.after(0, self._update_text_widget, message)

    def _update_text_widget(self, message):
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)  # 自动滚动到最后一行
        logging.info(message)

    def get_credentials(self):
        def submit():
            username = username_entry.get()
            password = password_entry.get()
            sleep_time = sleep_time_entry.get()
            if not username or not password or not sleep_time:
                messagebox.showerror("错误", "所有字段都是必填的")
            else:
                self.username = username
                self.password = password
                self.sleep_time = int(sleep_time)
                credentials_window.quit()
                credentials_window.destroy()

        credentials_window = tk.Toplevel(self)
        credentials_window.title("输入信息")

        tk.Label(credentials_window, text="用户名:").grid(row=0)
        tk.Label(credentials_window, text="密码:").grid(row=1)
        tk.Label(credentials_window, text="循环间隔时间(秒):").grid(row=2)

        username_entry = tk.Entry(credentials_window)
        password_entry = tk.Entry(credentials_window, show='*')
        sleep_time_entry = tk.Entry(credentials_window)

        username_entry.grid(row=0, column=1)
        password_entry.grid(row=1, column=1)
        sleep_time_entry.grid(row=2, column=1)

        submit_button = tk.Button(credentials_window, text="提交", command=submit)
        submit_button.grid(row=3, columnspan=2)

        credentials_window.mainloop()

    def run_script(self):
        self.get_credentials()
        if self.username and self.password and self.sleep_time:
            # 启动新的线程来运行脚本
            thread = Thread(target=self.start_login_process)
            thread.start()

    def start_login_process(self):
        while True:
            if os.path.exists(exit_flag_file):
                self.log_message("检测到退出标志，程序退出。")
                break
            self.login(self.username, self.password)
            time.sleep(self.sleep_time)

    def login(self, username, password):
        self.log_message("开始登录过程...")
        # 初始化Edge WebDriver
        options = webdriver.EdgeOptions()
        options.use_chromium = True
        options.add_argument("--start-maximized")
        options.add_argument("--headless")  # 启用无头模式
        driver = webdriver.Edge(options=options)

        try:
            # 验证网络连接状态
            driver.get("http://www.baidu.com")
            time.sleep(3)
            if "百度" in driver.title:
                self.log_message("网络连接成功")
                driver.quit()
                return
            else:
                self.log_message("网络连接失败")

            # 访问登录页面
            driver.get(login_url)

            # 等待页面加载
            time.sleep(3)

            # 输入用户名和密码
            username_input = driver.find_element(By.ID, "username")
            password_input = driver.find_element(By.ID, "password")

            username_input.send_keys(username)
            password_input.send_keys(password)

            # 点击登录按钮
            login_button = driver.find_element(By.ID, "login")
            login_button.click()

            # 等待登录完成
            time.sleep(5)

            # 验证登录成功
            if "srun_portal_success" in driver.current_url:
                self.log_message("登录成功")
            else:
                self.log_message("登录失败")
        except Exception as e:
            self.log_message(f"登录过程中出现异常: {e}")
        finally:
            # 关闭浏览器
            driver.quit()
            return

if __name__ == "__main__":
    app = Application()
    app.mainloop()
