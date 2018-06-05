# -*- coding: utf-8 -*-
'''
使用方法：
main.py <goods_file>, <sales_file>
goods_file:普通商品资料导出文件
sales_file:报表=>商品主题分析导出文件
执行完之后会创建 仓库.db，在sqliteStudio中打开后执行：
SELECT `商品$`.商品编码, `销量$`.`7天销量`, `商品$`.创建时间

FROM {oj `D:\杂\清仓\4.12\商品资料_2018-04-12_11-41-48.xlsx`.`商品$` `商品$` LEFT OUTER JOIN `D:\杂\清仓\4.12\商品资料_2018-04-12_11-41-48.xlsx`.`销量$` `销量$` ON `商品$`.商品编码 = `销量$`.商品编号}
WHERE (`商品$`.备注 Not Like '%清%' And `商品$`.备注 Not Like '%收%' And `商品$`.备注 Not Like '%过低%') AND (`销量$`.`7天销量`<2) OR (`商品$`.备注 Is Null) AND (`销量$`.`7天销量`<2)
'''
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import sys
import sqlite3
from datetime import datetime, date, timedelta

db_name = u'仓库.db'
goods_file = sys.argv[1]
sales_file = sys.argv[2]
stock_file = sys.argv[3]
conn = sqlite3.connect(db_name)

def convert_xls_to_db():
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

#convert_xls_to_db()
writer = pd.ExcelWriter(u'结果.xlsx')


t = date.today()   # 仅获取日期
d = timedelta(30)
month_ago =  t -d


# 销量过低商品
sql = u"""SELECT  g.商品编码, g.创建时间, g.备注, s.[7天销量], s.[15天销量], t.数量, g.createTime
  FROM goods as g, sales as s, stock as t 
  Where g.商品编码=s.商品编号 and g.商品编码=t.商品编码 and
   t.库存类型='仓位' and
   t.数量 >0 and
   s.[7天销量]<=2 and
   (g.备注 is null or 
   g.备注 Not Like '%%过低%%' and 
   g.备注 Not Like '%%清%%'and 
   g.备注 Not Like '%%收%%')and 
    g.createTime<Date('%s')""" % month_ago
df = pd.read_sql_query(sql, conn)
df.to_excel(writer, u"销量过低",  index=False)

# 清仓也清不动，直接下架报废的商品
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
