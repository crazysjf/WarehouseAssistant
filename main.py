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
import sqlite3
from datetime import datetime, date, timedelta
import getopt

db_name = u'仓库.db'
conn = sqlite3.connect(db_name)

def usage():
    print u'''
        main.py -g <goods_file> <sales_file> <stock_file>
        生成模式，读取文件生成数据库
        
        main.py
        计算产生结果报表'''


def convert_xls_to_db(goods_file, sales_file, stock_file):
    # 处理商品表
    # 需要转换日期格式，否则sql查询日期比较会出问题。
    df = pd.read_excel(goods_file)
    date = df[u"创建时间"]

    def str_to_datetime(s):
        return datetime.strptime(s, "%Y/%m/%d %H:%M:%S")
    r_date = map(str_to_datetime, date)
    df['CreateTime'] = r_date
    df.to_sql('goods', conn, if_exists="replace")

    # 处理销量列表
    df = pd.read_excel(sales_file)
    df.to_sql('sales', conn, if_exists="replace")

    # 处理库存列表
    df = pd.read_excel(stock_file)
    df.to_sql('stock', conn, if_exists="replace")

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
            convert_xls_to_db(args[0], args[1], args[2])
        sys.exit()

#convert_xls_to_db()
writer = pd.ExcelWriter(u'结果.xlsx')

t = date.today()   # 仅获取日期
d = timedelta(30)
month_ago =  t -d

# 半价清仓
# 上架超过30天，所有SKU的7天销量为0的宝贝，以款为单位，不是以SKU为单位
sql = u"""SELECT  g.款式编码, g.商品名, sum(s.[7天销量]) as [7天销量汇总], sum(s.[15天销量]) as [15天销量汇总], g.备注, sum(t.数量) as [库存汇总], g.createTime
  FROM goods as g, sales as s, stock as t 
  Where g.商品编码=s.商品编号 and g.商品编码=t.商品编码 and
   t.库存类型='仓位' and
   t.数量 >0 and
   (select sum(s1.[7天销量]) from sales s1 where s1.商品款号 = s.商品款号) = 0 and
    g.createTime<Date('%s') group by g.款式编码""" % month_ago
df = pd.read_sql_query(sql, conn)
df.to_excel(writer, u"半价清仓",  index=False)

# 数据保存至DB中，供之后查询使用
# pandas的to_sql有bug，此时不能使用含有中文的列名，必须替换为英文名。参考：https://stackoverflow.com/questions/33337798/unicodeencodeerror-when-using-pandas-method-to-sql-on-a-dataframe-with-unicode-c
df.columns = ['code', 'name', 'sum_7', 'sum_15', 'notes', 'sum_stock', 'createTime']
df.to_sql('clearance', conn, if_exists="replace")

# 销量过低SKU
# 上架超过30天，周销<=2，且不包括在清仓处理中 的SKU
sql = u"""SELECT  g.商品编码, g.备注, s.[7天销量], s.[15天销量], t.数量, g.createTime
  FROM goods as g, sales as s, stock as t
  Where g.商品编码=s.商品编号 and g.商品编码=t.商品编码 and
   t.库存类型='仓位' and
   t.数量 >0 and
   s.[7天销量]<=2 and
   (g.备注 is null or 
   g.备注 Not Like '%%过低%%' and 
   g.备注 Not Like '%%销低%%' and    
   g.备注 Not Like '%%清%%'and 
   g.备注 Not Like '%%收%%')and
    g.款式编码 not in (select code from clearance) and 
    g.createTime<Date('%s')""" % month_ago
#print sql
df = pd.read_sql_query(sql, conn)
df.to_excel(writer, u"销量过低",  index=False)


# 清仓也清不动，直接下架报废的商品
# TODO：该条在新算法中无效
sql = u"""SELECT  g.商品编码, g.创建时间, g.备注, s.[7天销量], s.[15天销量], t.仓位, t.数量, g.商品名, g.createTime
  FROM goods as g, sales as s, stock as t 
  Where g.商品编码=s.商品编号 and g.商品编码=t.商品编码 and
   t.库存类型='仓位' and
   t.数量 >0 and
   g.商品名 Like '清仓%%' and
   s.[7天销量]=0"""

df = pd.read_sql_query(sql, conn)
df.to_excel(writer, u"下架报废", index=False)

writer.save()


def gen_remark_imort_file():
    '''生成备注导入文件'''
    writer = pd.ExcelWriter(u'清仓备注导入.xlsx')
    sql = u"""SELECT g.商品编码, g.备注, g.款式编码 from goods as g WHERE
    g.款式编码 in (select code from clearance)"""
    df = pd.read_sql_query(sql, conn)



    df.to_excel(writer,  index=False)
    writer.save()

gen_remark_imort_file()