
import clearance_assistant.utils as utils
import sys
from openpyxl import load_workbook
import openpyxl.styles as sty
import clearance_assistant.web_operator as web_operator

def usage():
    print('''
py clearance_assistannt.py <working_dir>

working_dir:仓管助手生成的结果文件夹。
''')


if len(sys.argv) == 1:
    print("\nError: 必须有1个参数用于指定文件夹名称")
    usage()
    exit(-1)

dir = sys.argv[1]
file = dir + "//结果//结果.xlsx"

wb = load_workbook(file)
ws = wb['半价清仓（可移仓）']

# 插入原价列和清仓价列
orig_price_cn = utils.ws_get_column_cn(ws, "原价")
if orig_price_cn == None:
    ws.cell(row=1, column=ws.max_column + 1).value = "原价"
    orig_price_cn = ws.max_column + 1


clearance_price_cn = utils.ws_get_column_cn(ws, "清仓价")
if clearance_price_cn == None:
    ws.cell(row=1, column=ws.max_column + 1).value = "清仓价"
    clearance_price_cn = ws.max_column + 1

wo = web_operator.WebOperator()
wo.meizhe_start_operation()


for i in range(2, ws.max_row + 1):
    code = ws.cell(row=i, column=1).value

    # 仅处理清仓价不为空的行
    clearance_price = ws.cell(row=i, column=clearance_price_cn).value
    if clearance_price != None:
        continue

    print("正要设置：%d行，%s，按任意键继续：" % (i, code))
    input()

    ret = wo.meizhe_set_clearance_price_for_one_good(code)
    if ret == None:
        print("未找到商品")
        (orig_price, clearance_price) = ("未找到", "未找到")
    else:
        print("原价：%.2f，清仓价：%d" % (ret))
        (orig_price, clearance_price) = ret
    ws.cell(row=i, column=orig_price_cn).value = orig_price
    ws.cell(row=i, column=clearance_price_cn).value = clearance_price

    while(True):
        try:
            wb.save(file)
            break
        except IOError:
            input("文件无法保存，关掉其他应用后重试")



#wb.save(file)
wb.close()
exit(0)


#
# chrome_options = Options()
# chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
# driver = webdriver.Chrome(chrome_options=chrome_options)
#
# # 默认等待时间10秒
# driver.implicitly_wait(10)


# 进入活动管理页面
# driver.get("https://meizhe.meideng.net/huodong/list")

# 注意选择子的使用，必须保证在两个界面（第一次搜索和之后）都能使用
# search_box_ele = driver.find_element_by_css_selector("input.mz-form-control.mz-input")
# print(search_box_ele)
# print(search_box_ele.text)
#
# search_box_ele.clear()
# search_box_ele.send_keys("11008-6862" + Keys.RETURN)
# #main-content > div:nth-child(2) > div.mz-nav-block > ul > li.pull-right > form > input
#
# ele = driver.find_element_by_css_selector("div.final-price input")
#
# # 获取原价
# orig_price = ele.get_attribute("value")
#
#
# # 发送10次删除键
# ele.send_keys(Keys.BACKSPACE * 10 )
#
# clearance_price = utils.calc_clearance_price(orig_price)
# ele.send_keys(clearance_price)
#
# summit_button  = driver.find_element_by_css_selector("div.fast-submit a.btn-primary")
#
# #main-content > div:nth-child(2) > div.mz-edit-all-items > ul > li > ul:nth-child(2) > li > div.mz-row.mz-discountable-row > div.mz-col-md-0.decrease > input[type=text]