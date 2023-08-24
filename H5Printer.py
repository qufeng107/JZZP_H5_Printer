import sys
import os
from tkinter import *
import threading
import time
from h5_listener import h5_listener
from receipt_printer import receipt_printer
import fasteners
import selenium.webdriver as webdriver
from selenium.common.exceptions import NoSuchElementException


# 数据读写锁
data_lock = threading.Lock()

# 线程
threads = []

# 创建一个Chrome浏览器实例
driver = webdriver.Chrome()


# 读取配置文件
def readConfig():
    if not os.path.exists('./config.ini'):
        sys.exit(0)  # 结束程序
    config = {}
    # 读取config文件，获取模板的每个输入框的对应方式
    with open('./config.ini', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            # print(line)
            if line[0] == "#":
                continue
            if '=' in line:
                data = line.strip().split('=')
                config[data[0]] = data[1]
    print(config)
    return config


# 启动子线程
def start_threads():
    with data_lock:
        shared_data['running'] = True
    
    threads.append(threading.Thread(target=h5_listener, args=(shared_data, data_lock)))
    threads.append(threading.Thread(target=receipt_printer, args=(shared_data, data_lock)))

    for thread in threads:
        thread.start()


# 暂停子线程
def stop_threads():
    with data_lock:
        shared_data['running'] = False
        shared_data['frequency'] = 0.01
    


# 更新GUI
def update_gui(status_var, url_var, current_code_var, print_status_var, previous_code_var):
    status_var.set('Status: Running' if shared_data['running'] else 'Status: Stopped')
    url_var.set('Current Url: ' + shared_data['url'])
    current_code_var.set('Current Take Code: ' + shared_data['current_code'])
    print_status_var.set('Print Status: Printing' if shared_data['print_flag'] else 'Print Status: Printed')
    previous_code_var.set('Previous Take Code: ' + shared_data['previous_code'])
    root.after(1000, update_gui, status_var, url_var, current_code_var, print_status_var, previous_code_var)  # 每秒更新一次


# 当窗口关闭时
def on_close():
    stop_threads()  # 停止所有线程

    # 等待所有子线程完成
    for thread in threads:
        thread.join()

    driver.quit() # 关闭浏览器driver
    pid_lock.release()  # 释放锁
    root.destroy()  # 销毁窗口
    sys.exit(0)  # 结束程序


# def restart():
    
#     with data_lock:
#         if shared_data['restart_flag']:
#             previous_driver = shared_data['driver']
#             # 关闭浏览器
#             try:
#                 # 尝试关闭
#                 previous_driver.quit()
#             except WebDriverException:
#                 print("Browser has been closed")
#             # 创建一个Chrome浏览器实例
#             new_driver = webdriver.Chrome()
#             shared_data['driver'] = new_driver
#             # 打开一个网页
#             new_driver.get(h5_url)
#             # 以全屏模式打开Chrome浏览器
#             new_driver.fullscreen_window()
#         else:
#             shared_data['restart_flag'] = True



# 读取配置文件

config = readConfig()

h5_url = ''
frequency = 2
restart_flag = False

# 读取监听url
if config['url'] == '':
    sys.exit(0)  # 结束程序
else:
    h5_url = config['url']
    print(config['url'])

if config['time'] != '':
    frequency = config['time']



# 打开一个网页
driver.get(h5_url)
# 以全屏模式打开Chrome浏览器
driver.fullscreen_window()


# 全局共享变量
shared_data = {
    'driver': driver,
    'url': h5_url,
    'current_code': '',
    'previous_code': '',
    'print_flag': False,
    'running' : True,
    'frequency' : frequency,
    'restart_flag' : restart_flag,
    'receipt' : {},
    'new_code_event': threading.Event()
}


# 限制同时只能运行一个程序，禁止多开
# 利用文件锁技术，事先选定一个文件作为锁，运行第一个进程时锁住此文件
# 再次运行程序时检测文件此是否被锁定，若被锁定就说明已有一个程序正在运行
pid_lock = fasteners.InterProcessLock('./H5Printer.lock')
gotten = pid_lock.acquire(blocking=False)
if not gotten:
    print("Another instance of this application currently running.")
    sys.exit(1)


# GUI
root = Tk()
root.geometry('700x350')  # 设置窗口的宽为300，高为200
root.minsize(350, 250)  # 设置窗口的最小宽度为300，最小高度为200
root.title('H5 Printer')  # 设置窗口的标题
root.protocol("WM_DELETE_WINDOW", on_close)  # 当窗口关闭时调用on_close函数

# 设置文本
status_var = StringVar()
url_var = StringVar()
current_code_var = StringVar()
previous_code_var = StringVar()
print_status_var = StringVar()



Button(root, 
       text="Stop/Start", 
       command=lambda: start_threads() if not shared_data['running'] else stop_threads(),
       bg="lightblue",
       fg="orange",
       padx=10,
       pady=10,
       font=("Arial", 20, "bold")
       ).pack()
Label(root, 
      textvariable=status_var,
      font=("Arial", 20, "bold"),
      fg="red",
      ).pack()
Label(root, 
      textvariable=url_var,
      font=("Arial", 15)
      ).pack()
Label(root, 
      textvariable=current_code_var,
      font=("Arial", 15, "bold")
      ).pack()
Label(root, 
      textvariable=print_status_var,
      font=("Arial", 15)
      ).pack()
Label(root, 
      textvariable=previous_code_var,
      font=("Arial", 15)
      ).pack()
# Button(root, 
#        text="Restart H5", 
#        command=restart(),
#        bg="lightblue",
#        fg="orange",
#        padx=10,
#        pady=10,
#        font=("Arial", 15, "bold")
#        ).pack()

update_gui(status_var, url_var, current_code_var, print_status_var, previous_code_var)


# 自动开始监听
start_threads()

root.mainloop()