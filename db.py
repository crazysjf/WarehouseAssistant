# -*- coding: utf-8 -*-

import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from datetime import datetime, date, timedelta
import sqlite3
import utils
#db_name = u'仓库.db'
conn = None
import re

def init():
    global conn
    conn = sqlite3.connect(utils.get_db_file())

def convert_xls_to_db(goods_file, sales_file, stock_file, tb_assistant_file):
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

    # 处理淘宝助理文件
    if tb_assistant_file != None:
        df = pd.read_excel(tb_assistant_file)
        df.to_sql('tb_assistant', conn, if_exists="replace")


# 各操作判断标准参考readme.txt

# 半价清仓
sql_clearance = u"""SELECT  g.款式编码, g.商品名, sum(s.[7天销量]) as [7天销量汇总], sum(s.[15天销量]) as [15天销量汇总], g.备注, sum(t.数量) as [库存汇总], g.createTime
      FROM goods as g, sales as s, stock as t 
      Where g.商品编码=s.商品编号 and g.商品编码=t.商品编码 and
       t.库存类型='仓位' and
       t.数量 >0 and
        g.备注 Not Like '%%清%%'and 
       (select sum(s1.[7天销量]) from sales s1 where s1.商品款号 = s.商品款号) < 2 and
        g.createTime<Date('%s') group by g.款式编码""" % (date.today() - timedelta(30))


# 销量过低SKU
sql_sales_too_low = u"""SELECT  g.商品编码, g.备注, s.[7天销量], s.[15天销量], t.数量,  g.createTime, t.仓位
      FROM goods as g, sales as s, stock as t
      Where g.商品编码=s.商品编号 and g.商品编码=t.商品编码 and
       t.库存类型='仓位' and
       t.数量 >0 and
       s.[7天销量]<=2 and
       s.[15天销量] <= 5 and
       (g.备注 is null or 
       g.备注 Not Like '%%过低%%' and 
       g.备注 Not Like '%%销低%%' and    
       g.备注 Not Like '%%清%%'and 
       g.备注 Not Like '%%收%%')and
        g.款式编码 not in (select code from clearance) and 
        g.createTime<Date('%s')""" % (date.today() - timedelta(30))

# 清仓商品销量：备注包含“清”字，且销量>0的款
sql_sales_clearance = u"""SELECT  g.商品编码, g.备注, s.[7天销量], s.[15天销量], t.数量, g.createTime
      FROM goods as g, sales as s, stock as t
      Where g.商品编码=s.商品编号 and g.商品编码=t.商品编码 and
       (s.[7天销量] > 0 or s.[15天销量] > 0) and 
       g.备注 Like '%%清%%'"""

# 可下架商品
sql_off_shelf =  u"""SELECT  g.款式编码, g.商品名, sum(s.[7天销量]) as [7天销量汇总], sum(s.[15天销量]) as [15天销量汇总], g.备注, sum(t.数量) as [库存汇总], g.createTime, t.仓位
      FROM goods as g, sales as s, stock as t 
      Where g.商品编码=s.商品编号 and g.商品编码=t.商品编码 and
       t.库存类型='仓位' and
       t.数量 >0 and
       g.备注 Like '%%清%%' and
       (select sum(s1.[15天销量]) from sales s1 where s1.商品款号 = s.商品款号) = 0
        group by g.款式编码"""


# 有库存未上架商品：有库存，但是线上状态为已下架
sql_not_on_shelf =  u"""SELECT g.款式编码, sum(t.数量) as [库存汇总],  t.仓位, ta.放入仓库 as 是否下架
      FROM stock as t, tb_assistant as ta, goods as g 
      Where t.商品编码=g.商品编码 and g.款式编码=ta.商家编码 and 
       t.库存类型='仓位' and
       ta.放入仓库=2
       group by g.款式编码"""


# 可移仓款
# 由于本次的清仓和销低还没有导入，本次处理被判断为清仓或者销低的款不在此列。
# 如果本次清仓和销低如果需要移仓，直接看清仓和销低表即可。
def getShelfMovableGoods():
    '''返回dataframe'''

    # 查找所有备注里面有“清”、“收”、“销低”（统称为关键词）的款号
    sql =  u"""SELECT  g.款式编码, g.商品编码, sum(s.[7天销量]) as [7天销量汇总], sum(s.[15天销量]) as [15天销量汇总], g.备注, sum(t.数量) as [库存汇总], g.createTime, t.仓位
          FROM goods as g, sales as s, stock as t 
          Where g.商品编码=s.商品编号 and g.商品编码=t.商品编码 and
           t.库存类型='仓位' and
           t.数量 >0 and
           (g.备注 Like '%%清%%' or
           g.备注 Like '%%销低%%' or
           g.备注 Like '%%收%%')
           group by g.款式编码"""
    df = pd.read_sql_query(sql, conn)

    # 只有所有SKU的备注中都包含有关键词，整个款才能被移仓。
    # 筛掉只部分SKU包含关键词的款。
    for code in df['款式编码']:
        sql2 = """SELECT 款式编码, 商品编码, 备注 
        FROM goods 
        WHERE 款式编码='%s'""" % (code)
        df2 = pd.read_sql_query(sql2, conn)
        isMovable = True
        for n in df2['备注']:
            # 以防备注为None，后续in判断出现异常
            if n == None:
                n = ""

            if (not '清' in n) and \
                (not '销低' in n) and \
                (not '收' in n):
                isMovable = False

        # 过滤掉不可移动的款号
        if not isMovable:
            df = df.loc[df['款式编码'] != code]

    # 过滤掉仓位以"Q-Q-"+数字开头的
    df = df[df['仓位'].map(lambda c: True if re.match(r'^Q-Q-[0-9]+-.*',c) == None else False)]

    # 删掉商品编码列
    df.drop('商品编码', axis = 1, inplace=True)

    return df

def get_multi_goods_in_one_slot():
    '''
    获取一仓多货情况。
    
    :return: 描述一仓多货情况的df
    '''
    result_df = pd.DataFrame(columns=['仓位','款号'])

    _, _, stock_file, _ = utils.get_source_files()
    df = pd.read_excel(stock_file)

    # 仅保留库存类型为仓位的行
    df = df.loc[df['库存类型']=='仓位']

    # 去重后的仓位列表
    slots = df['仓位'].unique()
    for s in slots:
        tmp = df.loc[df['仓位']==s]
        # 同一仓位的所有商品编码
        codes = tmp['商品编码']

        # 返回款号：需要考虑带尺码的情况
        def split_code(s):
            m = re.match(r'(.*)-[^-SMLXsmlx]+(-[SMLXsmlx]+)*$', s)
            if m != None:
                return m.group(1)
            else:
                return s

        style_codes = set(map(split_code, codes))
        if len(style_codes) > 1:
            result_df = result_df.append({'仓位':s, '款号':style_codes}, ignore_index=True)

    return result_df

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

    # 清仓款
    df[u'仓位'] = df['款式编码'].map(lambda c: dict[c])
    df.to_excel(writer, "半价清仓（可移仓）",  index=False)

    # 销量过低SKU
    df = pd.read_sql_query(sql_sales_too_low, conn)
    df.to_excel(writer, "销量过低",  index=False)

    # 清仓商品销量
    df = pd.read_sql_query(sql_sales_clearance, conn)
    df.to_excel(writer, "清仓商品销量",  index=False)

    # 可下架款
    df = pd.read_sql_query(sql_off_shelf, conn)
    # TODO：此处要加入对备注中的清仓日期判断：清仓时间在规定可时间以上才入选。目前是只要备注有清字就入选
    df.to_excel(writer, "可下架款",  index=False)


    df = getShelfMovableGoods()
    df.to_excel(writer, "可移仓款（不包括本次清仓和销低款）",  index=False)


    # 有库存未上架款
    try:
        df = pd.read_sql_query(sql_not_on_shelf, conn)
        df.to_excel(writer, "有库存未上架款", index=False)
    except:
        pass

    # 一仓多货
    df = get_multi_goods_in_one_slot()
    df.to_excel(writer, "一仓多货",  index=False)

    writer.save()



def gen_remark_import_file():
    '''生成清仓备注导入文件'''
    sql = u"""SELECT g.商品编码, g.备注, g.款式编码 from goods as g WHERE
    g.款式编码 in (select code from clearance)"""
    df = pd.read_sql_query(sql, conn)

    # 在备注前加入"清6.7，"字样
    d = datetime.now()
    # 数据库中读出的dataframe列名不能使用unicode做索引
    df['备注'] = df['备注'].map(lambda a: u'清%d.%d.%d, %s' %(d.year % 2000, d.month, d.day, a if a != None else ""))

    # 计算款数
    c = df['款式编码'].value_counts()
    writer = pd.ExcelWriter(utils.get_output_full_file_path('清仓备注导入-%d个款.xlsx' % c.size))

    # 款式编码无需导入
    df.pop('款式编码')

    df.to_excel(writer,  index=False)
    writer.save()

    # 生成销量过低备注导入文件
    df = pd.read_sql_query(sql_sales_too_low, conn)
    df2 = pd.DataFrame()
    df2[u'商品编码'] = df['商品编码']
    df2[u'备注'] = df['备注'].map(lambda a: u'销低%d.%d.%d, %s' %(d.year % 2000, d.month, d.day, a if a != None else ""))

    writer = pd.ExcelWriter(utils.get_output_full_file_path('销低备注导入-%d个SKU.xlsx' % df2[u'商品编码'].value_counts().size))
    df2.to_excel(writer,  index=False)
    writer.save()

