# -*- coding: utf-8 -*-
'''
使用方法：
py -3 main.py <goods_file>, <sales_file>, <stock_file>
注意用python3执行。
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
import utils

def usage():
    print('''
py main.py -g <working_dir>
生成模式，读取working_dir里面的文件生成数据库。
        
working_dir里面必须有3个文件：
商品资料*.xlsx -- 普通商品资料导出文件
商品综合分析*.xlsx -- 商品主题分析导出文件
箱及仓位库存*.xlsx -- 箱及仓位库存导出文件
        
        
py main.py <working_dir>
计算产生结果报表
''')


try:
    options,args = getopt.getopt(sys.argv[1:],"thg",["help"])
except getopt.GetoptError:
    usage()
    sys.exit()

if len(args) != 1:
    print("Error: 必须有1个参数用于指定文件夹名称")
    usage()
    exit(-1)

utils.set_file_dir(args[0])

if len(options) != 0:
    for name,value in options:
        if name in ("-h","--help"):
            usage()
        elif name in ("-g"):
            # 生成模式
            if len(args) != 1:
                print(u"参数数量必须是1个")
                exit(-1)
            else :
                db.init()
                f1,f2,f3,f4 = utils.get_source_files()
                db.convert_xls_to_db(f1, f2, f3, f4)
                # 判断是否有淘宝助手文件
                exit(0)
        elif name in ("-t"):
            db.get_multi_goods_in_one_slot()



else:
    utils.set_file_dir(args[0])
    db.init()
    db.gen_reresult_file()
    db.gen_remark_import_file()

    # for dev test
    #db.get_one_good_in_multiple_slots()
    exit(0)
