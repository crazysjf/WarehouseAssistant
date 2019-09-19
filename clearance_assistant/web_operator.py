
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.keys import Keys
import clearance_assistant.utils as utils
import time

class WebOperator():
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self._driver = webdriver.Chrome(chrome_options=chrome_options)

        # 默认等待时间10秒
        self._driver.implicitly_wait(10)

    def meizhe_start_operation(self):
        # 进入活动管理页面
        self._driver.get("https://meizhe.meideng.net/huodong/list")

    def meizhe_set_clearance_price_for_one_good(self, code):
        """
        
        :param code: 
        :return: 返回（原价, 清仓价)，如果没有找到任何商品，返回None 
        """
        # 注意选择子的使用，必须保证在两个界面（第一次搜索和之后）都能使用
        search_box_ele = self._driver.find_element_by_css_selector("input.mz-form-control.mz-input")

        search_box_ele.clear()
        search_box_ele.send_keys(code + Keys.RETURN)
        # main-content > div:nth-child(2) > div.mz-nav-block > ul > li.pull-right > form > input


        # 这里需要判断有没有查找到相应的商品。
        # 需要通过 div.mz-edit-all-items div.mz-alert 的style属性判断
        # 该div用于显示“没有找到任何打折商品”的提示。
        # 无论有没有找到商品，该div都会存在，只是找到商品的情况下style会被设为display:none

        # 页面使用ajax加载，警告框似乎一直存在，此处只能等待
        time.sleep(1)
        allert_div = self._driver.find_element_by_css_selector("div.mz-edit-all-items div.mz-alert")

        # 有警告框（style="display: none 不存在），就不用继续了
        if "none" not in allert_div.get_attribute("style"):
            return None

        price_input = self._driver.find_element_by_css_selector("div.final-price input")

        # 获取原价
        orig_price = float(price_input.get_attribute("value"))

        price_input.clear()

        clearance_price = utils.calc_clearance_price(orig_price)
        price_input.send_keys(str(clearance_price))

        summit_button = self._driver.find_element_by_css_selector("div.fast-submit a.btn-primary")
        summit_button.click()

        return (orig_price, clearance_price)
