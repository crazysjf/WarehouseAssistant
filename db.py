# -*- coding: utf-8 -*-

import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from datetime import datetime, date, timedelta
import sqlite3
import utils
#db_name = u'仓库.db'
conn = None

def init():
    global conn
    conn = sqlite3.connect(utils.get_db_file())
def convert_xls_to_db(goods_file, sales_file, stock_file):
    # 处理商品表
    # 需要转换日期格式，否则sql查询日期比较会出问题。
    df = pd.read_excel(goods_file)
    date = df[u"创建时间"]

    def str_to_datetime(s):
        return datetime.strptime(s, "%Y/%m/%d %H:%M:%S")
    r_date = list(map(str_to_datetime, date))
    df['CreateTime'] = r_date
    df.to_sql('goods', conn, if_exists="replace")

    # 处理销量列表
    df = pd.read_excel(sales_file)
    df.to_sql('sales', conn, if_exists="replace")

    # 处理库存列表
    df = pd.read_excel(stock_file)
    df.to_sql('stock', conn, if_exists="replace")


# 半价清仓
# 上架超过30天，所有SKU的7天销量为0的宝贝，以款为单位，不是以SKU为单位
sql_clearance = u"""SELECT  g.款式编码, g.商品名, sum(s.[7天销量]) as [7天销量汇总], sum(s.[15天销量]) as [15天销量汇总], g.备注, sum(t.数量) as [库存汇总], g.createTime
      FROM goods as g, sales as s, stock as t 
      Where g.商品编码=s.商品编号 and g.商品编码=t.商品编码 and
       t.库存类型='仓位' and
       t.数量 >0 and
       (select sum(s1.[7天销量]) from sales s1 where s1.商品款号 = s.商品款号) = 0 and
        g.createTime<Date('%s') group by g.款式编码""" % (date.today() - timedelta(30))

#
# 销量过低SKU
# 上架超过30天，周销<=2，且不包括在清仓处理中 的SKU
sql_sales_to_low = u"""SELECT  g.商品编码, g.备注, s.[7天销量], s.[15天销量], t.数量, g.createTime
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
        g.createTime<Date('%s')""" % (date.today() - timedelta(30))

def gen_reresult_file():
    writer = pd.ExcelWriter(utils.get_output_full_file_path('结果.xlsx'))

    # 查询清仓SKU
    df = pd.read_sql_query(sql_clearance, conn)

    # 数据保存至DB中，供之后查询使用
    # pandas的to_sql有bug，此时不能使用含有中文的列名，必须替换为英文名。参考：https://stackoverflow.com/questions/33337798/unicodeencodeerror-when-using-pandas-method-to-sql-on-a-dataframe-with-unicode-c
    df2 = df.copy()
    df2.columns = ['code', 'name', 'sum_7', 'sum_15', 'notes', 'sum_stock', 'createTime']
    df2.to_sql('clearance', conn, if_exists="replace")

    # 把所有仓位对应上去
    dict = {}
    for c in df['款式编码']:
        # 在库存表中有的行只有商品编码没有款式编码，必须借助商品表中转
        sql = u"""SELECT distinct t.仓位
              FROM goods as g, stock as t
          Where t.商品编码=g.商品编码 and 
          g.款式编码='%s' and 
          t.库存类型='仓位'""" % c
        df1 = pd.read_sql_query(sql, conn)
        s = ""
        for r in df1['仓位']:
            s = s + "%s, " % r
        dict[c] = s

    df[u'仓位'] = df['款式编码'].map(lambda c: dict[c])
    df.to_excel(writer, u"半价清仓",  index=False)

    # 查询销量过低SKU
    df = pd.read_sql_query(sql_sales_to_low, conn)
    df.to_excel(writer, u"销量过低",  index=False)

    writer.save()


def gen_remark_import_file():
    '''生成清仓备注导入文件'''
    sql = u"""SELECT g.商品编码, g.备注, g.款式编码 from goods as g WHERE
    g.款式编码 in (select code from clearance)"""
    df = pd.read_sql_query(sql, conn)

    # 在备注前加入"清6.7，"字样
    d = datetime.now()
    # 数据库中读出的dataframe列名不能使用unicode做索引
    df['备注'] = df['备注'].map(lambda a: u'清%d.%d, %s' %(d.month, d.day, a if a != None else ""))

    # 计算款数
    c = df['款式编码'].value_counts()
    writer = pd.ExcelWriter(utils.get_output_full_file_path('清仓备注导入-%d个款.xlsx' % c.size))

    # 款式编码无需导入
    df.pop('款式编码')

    df.to_excel(writer,  index=False)
    writer.save()

    # 生成销量过低备注导入文件
    df = pd.read_sql_query(sql_sales_to_low, conn)
    df2 = pd.DataFrame()
    df2[u'商品编码'] = df['商品编码']
    df2[u'备注'] = df['备注'].map(lambda a: u'销低%d.%d, %s' %(d.month, d.day, a if a != None else ""))

    writer = pd.ExcelWriter(utils.get_output_full_file_path('销低备注导入-%d个SKU.xlsx' % df2[u'商品编码'].value_counts().size))
    df2.to_excel(writer,  index=False)
    writer.save()

