import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
import configparser

# 配置
login_url = "http://10.0.0.55/srun_portal_pc?ac_id=8&srun_wait=1&theme=bit"
exit_flag_file = 'exit_flag.txt'
config_file = 'config.ini'

# 设置日志记录配置
logging.basicConfig(
    filename='login_script.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def manual_input_credentials_2():
    def submit():
        username = username_entry.get()
        password = password_entry.get()
        sleep_time = sleep_time_entry.get()
        if not username or not password or not sleep_time:
            messagebox.showerror("错误", "所有字段都是必填的")
        else:
            root.quit()
            root.destroy()
            credentials['username'] = username
            credentials['password'] = password
            credentials['sleep_time'] = int(sleep_time)

    credentials = {}
    root = tk.Tk()
    root.title("输入信息")

    tk.Label(root, text="用户名:").grid(row=0)
    tk.Label(root, text="密码:").grid(row=1)
    tk.Label(root, text="循环间隔时间(秒):").grid(row=2)

    username_entry = tk.Entry(root)
    password_entry = tk.Entry(root, show='*')
    sleep_time_entry = tk.Entry(root)

    username_entry.grid(row=0, column=1)
    password_entry.grid(row=1, column=1)
    sleep_time_entry.grid(row=2, column=1)

    submit_button = tk.Button(root, text="提交", command=submit)
    submit_button.grid(row=3, columnspan=2)

    root.mainloop()

    if 'username' not in credentials or 'password' not in credentials or 'sleep_time' not in credentials:
        messagebox.showerror("错误", "所有字段都是必填的")
        exit(1)
    return credentials


def manual_input_credentials():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    username = simpledialog.askstring("输入", "请输入用户名:")
    if username is None:
        messagebox.showerror("错误", "用户名不能为空")
        root.quit()
        exit(1)

    password = simpledialog.askstring("输入", "请输入密码:", show='*')
    if password is None:
        messagebox.showerror("错误", "密码不能为空")
        root.quit()
        exit(1)

    root.quit()

    return username, password


def get_credentials():

    config = configparser.ConfigParser()
    if os.path.exists(config_file):
        credentials = {'username': '', 'password': '', 'sleep_time': 60}
        config.read(config_file)
        credentials['username'] = config.get('Credentials', 'username')
        credentials['password'] = config.get('Credentials', 'password')
        credentials['sleep_time'] = config.getint('Credentials', 'sleep_time')
        return credentials
    else:
        logging.error(f"Config file {config_file} not found.")
        # raise FileNotFoundError(f"Config file {config_file} not found.")
        credentials = manual_input_credentials_2()
        # username, password, sleep_time = manual_input_credentials_2()
        with open(config_file,'w') as configfile:
            # config['Credentials'] = {'username': username, 'password': password, 'sleep_time': sleep_time}
            config['Credentials'] = credentials
            config.write(configfile)
    return credentials

def login(username, password):
    logging.info("Starting login process")
    # 初始化Edge WebDriver
    options = webdriver.EdgeOptions()
    options.use_chromium = True
    options.add_argument("--start-maximized")
    options.add_argument("--headless")  # 启用无头模式
    driver = webdriver.Edge(options=options)

    try:
        # # 验证网络连接状态
        # driver.get("http://www.baidu.com")
        # time.sleep(2)
        # if "百度" in driver.title:
        #     logging.info("connect baidu success")
        #     driver.quit()
        #     return
        # else:
        #     logging.info("connect baidu fail")

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
        time.sleep(2)

        # 验证登录成功
        if "srun_portal_success" in driver.current_url:
            logging.info("login success")
        else:
            logging.info("login failed")
    except Exception as e:
        logging.error(f"Exception occurred during login process: {e}")
    finally:
        # 关闭浏览器
        driver.quit()
        return

if __name__ == "__main__":
    credentials = get_credentials()
    while True:
        if os.path.exists(exit_flag_file):
            logging.info("Exit flag detected. Exiting program.")
            break
        login(credentials['username'], credentials['password'])
        time.sleep(credentials['sleep_time'])
