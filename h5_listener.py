'''
Author: error: error: git config user.name & please set dead value or install git && error: git config user.email & please set dead value or install git & please set dead value or install git
Date: 2023-08-23 15:42:46
LastEditors: qufeng107 qufeng107@gmail.com
LastEditTime: 2023-08-31 19:55:31
FilePath: \JZZP_H5_Printer\h5_listener.py
Description: 

Copyright (c) 2023 by ${git_name_email}, All Rights Reserved. 
'''

import time
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.webdriver as webdriver









def h5_listener(shared_data, data_lock):

    error_msg = ""

    while True:
        # 检查软件状态
        running = shared_data['running']
        if running == False:
            shared_data['new_code_event'].set()
            print('Stopping Listening')
            break

        with data_lock:
            frequency = int(shared_data['frequency'])
            driver = shared_data['driver']
            h5_url = shared_data['url']

        try:
            driver.fullscreen_window()
        except Exception as e:
            pass
        # 监听网页
        h5_order_url = h5_url.replace('/menu', '/order')
        res = find_code(driver, h5_order_url)
        code = res[0]
        receipt = res[1]
        
        if code == '-1':
            error = receipt
            # print('new error= ', error)
            if 'Message: no such window: target window already closed' in error:
                try:
                    driver.quit()
                except Exception as e:
                    pass
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument("--force-device-scale-factor=1.5")
                driver = webdriver.Chrome(options=chrome_options)
                driver.get(h5_url)
                # 以全屏模式打开Chrome浏览器
                driver.fullscreen_window()
                # 更新shared_data的driver实例
                with data_lock:
                    shared_data['driver'] = driver


            if error not in error_msg:
                with open('log_listening.txt', 'a') as file:
                    now = datetime.now()
                    file.write('Time: ' + str(now) + '\n')
                    file.write('Error: ' + error + '\n')
                    file.write('\n===============================\n\n')
                    error_msg = error
                    # print('old error= ', error_msg)

            time.sleep(frequency)
            continue

        # 更新current_code
        with data_lock:
            # print("previous_code: " + shared_data['previous_code'])
            # print("current_code: " + shared_data['current_code'])
            if shared_data['current_code'] != code and str(code) != '0':
                shared_data['previous_code'] = shared_data['current_code']
                shared_data['receipt'] = receipt
                # print("previous_code: " + shared_data['previous_code'])
                # print("current_code: " + shared_data['current_code'])
                shared_data['current_code'] = code
                shared_data['print_flag'] = True
                shared_data['new_code_event'].set()

                with open('log_listening.txt', 'a') as file:
                    now = datetime.now()
                    file.write('Time: ' + str(now) + '\n')
                    file.write('Code: ' + str(code) + '\n')
                    file.write('success\n')
                    file.write('\n===============================\n\n')

        time.sleep(frequency)  # 每x秒检查一次
    
    print('Listening Stopped')



# 查找code
def find_code(driver, h5_url):
    receipt = {}

    # 检测focus网页
    # 判断当前网页是否为h5网址
    # print("Current Url: " + str(driver.current_url))

    try:
        if h5_url in driver.current_url and '/order/' in driver.current_url :
            # 搜索包含'Take Code'字符串的文本框
            # element = driver.find_element_by_xpath("//*[contains(text(), 'Take Code')]")
            # 将'Take Code'字符串保存到共享数据
            # code = element.text
            time.sleep(1)
            code = driver.find_elements('xpath','//*[@class="order-no"]')[0].text


            # 判断是否存在Show More按钮，存在则点击
            # try:
            #     element = driver.find_element('xpath','/html/body/div/div/div[2]/div[2]/div[4]/div[2]/div[4]/button')
            #     element.click()
            # except NoSuchElementException:
            #     1

            # receipt['name'] = driver.find_elements('xpath','//*[@class="title"]')
            # receipt['qty'] = driver.find_elements('xpath','//*[@class="qty"]')
            # receipt['price'] = driver.find_elements('xpath','//*[@class="number"]')
            # receipt['info'] = driver.find_elements('xpath','//*[@class="info"]')

            return code, receipt
            
        else:
            return '0', ""
        
    except Exception as e:
        return '-1', str(e)
