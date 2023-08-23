'''
Author: error: error: git config user.name & please set dead value or install git && error: git config user.email & please set dead value or install git & please set dead value or install git
Date: 2023-08-23 15:42:46
LastEditors: error: error: git config user.name & please set dead value or install git && error: git config user.email & please set dead value or install git & please set dead value or install git
LastEditTime: 2023-08-23 20:27:27
FilePath: \JZZP_H5_Printer\h5_listener.py
Description: 

Copyright (c) 2023 by ${git_name_email}, All Rights Reserved. 
'''

import time
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def h5_listener(shared_data, data_lock):
    while True:
        # 检查软件状态
        running = shared_data['running']
        if not running:
            time.sleep(1)
            break

        with data_lock:
            frequency = int(shared_data['frequency'])
            driver = shared_data['driver']
            h5_url = shared_data['url']

        # 监听网页
        res = find_code(driver, h5_url)
        code = res[0]
        receipt = res[1]
        if code == '-1':
            time.sleep(frequency)
            continue

        # 更新current_code
        with data_lock:
            # print("previous_code: " + shared_data['previous_code'])
            # print("current_code: " + shared_data['current_code'])
            if shared_data['current_code'] != code:
                shared_data['previous_code'] = shared_data['current_code']
                shared_data['receipt'] = receipt
                # print("previous_code: " + shared_data['previous_code'])
                # print("current_code: " + shared_data['current_code'])
                shared_data['current_code'] = code
                shared_data['print_flag'] = True
                shared_data['new_code_event'].set()

        time.sleep(frequency)  # 每x秒检查一次



# 查找code
def find_code(driver, h5_url):
    receipt = {}

    # 检测focus网页
    # 判断当前网页是否为h5网址
    # print("Current Url: " + str(driver.current_url))
    if 'https://tg2.weimember.cn/' in driver.current_url and '/order/' in driver.current_url :
        try:
            
            # 搜索包含'Take Code'字符串的文本框
            # element = driver.find_element_by_xpath("//*[contains(text(), 'Take Code')]")
            # 将'Take Code'字符串保存到共享数据
            # code = element.text
            try:
                time.sleep(1)
                code = driver.find_element('xpath','/html/body/div[1]/div/div[2]/div[1]/div[2]').text
                with open('log_listening.txt', 'a') as file:
                    now = datetime.now()
                    file.write('Time: ' + str(now) + '\n')
                    file.write('Code: ' + str(code) + '\n')
                    file.write('success\n')
                    file.write('\n===============================\n\n')
            except Exception as e:
                with open('log_listening.txt', 'a') as file:
                    now = datetime.now()
                    file.write('Time: ' + str(now) + '\n')
                    file.write('Error: ' + str(e) + '\n')
                    file.write('\n===============================\n\n')

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
        
        except Exception as e:
            return '-1', receipt

    else:
        return '-1', receipt