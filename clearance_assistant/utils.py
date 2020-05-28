
# def calc_clearance_price(orig_price):
#     '''
#     计算清仓价格。
#     :param orig_price:原价
#     :return:返回值也应该为文本字符串
#     '''
#     clearance_price = orig_price
#
#     orig_price = orig_price + 1
#     clearance_price = int(orig_price / 2)
#
#     # 如果为10的备注则把尾号改为9
#     if clearance_price % 10 == 0:
#         clearance_price = clearance_price - 1
#
#     # 最低价为16元
#     if clearance_price < 16:
#         clearance_price = 16
#
#     return clearance_price

def calc_clearance_price(orig_price):
    '''
    计算清仓价格。
    :param orig_price:原价 
    :return:返回值也应该为文本字符串 
    '''
    clearance_price = orig_price

    orig_price = orig_price + 1
    clearance_price = int(orig_price * 2 / 3)

    # 如果为10的备注则把尾号改为9
    if clearance_price % 10 == 0:
        clearance_price = clearance_price - 1

    # 最低价为16元
    if clearance_price < 16:
        clearance_price = 16

    return clearance_price


def ws_get_column_cn(ws, name):
    """
    从work sheet里面通过标题查找表头
    :param ws: 
    :param name: 
    :return: 
    """
    for c in range(1, ws.max_column + 1):
        v = ws.cell(row = 1, column=c).value
        if v == name:
            return c
    return None

if __name__ == "__main__":
    print(calc_clearance_price(12.4))
    print(calc_clearance_price(80.88))
    print(calc_clearance_price(79))
    print(calc_clearance_price(35.8))
    print(calc_clearance_price(42.8))
    print(calc_clearance_price(45.8))
