# -*- coding: utf-8 -*-
'''
使用方法：
main.py <goods_file>, <sales_file>, <stock_file>
goods_file:普通商品资料导出文件
sales_file:报表=>商品主题分析导出文件
stock_file:库存=>箱及仓位库存导出文件

执行之前先要更新聚水潭中的商品标题。不能在聚水潭中重新下载商品信息覆盖来做，这样会破坏聚合款的结构。需要从其他软件导出最新商品编码和标题的对应关系再导入。

执行完之后会创建 结果.xlsx。
'''

import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import sys
from datetime import datetime, date, timedelta
import getopt
import db


def usage():
    print u'''
        main.py -g <goods_file> <sales_file> <stock_file>
        生成模式，读取文件生成数据库
        
        main.py
        计算产生结果报表'''


try:
    options,args = getopt.getopt(sys.argv[1:],"hg",["help"])
except getopt.GetoptError:
    usage()
    sys.exit()

for name,value in options:
    if name in ("-h","--help"):
        usage()
    if name in ("-g"):
        if len(args) != 3:
            print u"参数数量必须是3个"
        else :
            db.convert_xls_to_db(args[0], args[1], args[2])
        sys.exit()

db.gen_reresult_file()
db.gen_remark_import_file()