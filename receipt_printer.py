
import time
from win32printing import Printer

def receipt_printer(shared_data, data_lock):

    while True:
        # 检查软件状态
        running = shared_data['running']
        if not running:
            break

        code = ''
        receipt = {}

        with data_lock:
            frequency = int(shared_data['frequency'])
            code = shared_data['current_code']
            receipt = shared_data['receipt']



        # 打印
        with data_lock:
            if shared_data['print_flag'] == True:
                print_code(code, receipt)
                shared_data['print_flag'] = False

        time.sleep(frequency)  # 每x秒检查一次




def print_code(code, receipt):

    print("Code = " + str(code))
    names = receipt['name']
    numbers = receipt['qty']
    prices = receipt['price']
    choices = receipt['info']

    total = prices[-1].text
    service_fee = ''
    dish_num = min(len(numbers),len(choices))

    if (dish_num + 2) == len(prices) :
        service_fee = prices[-2].text
    else:
        service_fee = "0.00"


    # print("dishes---------------")
    # for i in range(0, dish_num):
    #     print("dish name : " + names[i].text)
    #     print("choice : " + choices[i].text)
    #     print("number : " + numbers[i].text)
    #     print("price : " + prices[i].text)

    # print("---------------")
    # print("Service fee : " + service_fee)
    # print("Total Amount : " + total)

    # 调用打印机
    print("Printing new code: " + code)
    font_code = {
        "height": 22,
    }
    font_title = {
        "height": 14,
    }
    font_dish = {
        "height": 13,
    }
    font_total = {
        "height": 15,
    }

    with Printer(linegap=1) as printer:
        printer.text(f"Order ID: {code}", font_config=font_code, align="center")
        printer.text("--------------------------------------------------------------------------", font_config={"height":10}, align="center")
        printer.text("Qty    ItemName                             Price", font_config=font_title, align="left")
        for i in range(0, dish_num):
            printer.text(f"{numbers[i].text[1:]}x      {names[i].text} ({choices[i].text})", font_config=font_dish,align="left")
            printer.text(f"£ {prices[i].text} ",font_config=font_dish,align="right")
        printer.text("--------------------------------------------------------------------------", font_config={"height":10}, align="center")
        printer.text(f"Service Fee:    £{service_fee} ",font_config=font_total,align="right")
        printer.text(f"Total Amount:  £{total} ",font_config=font_total,align="right")
        printer.new_page()