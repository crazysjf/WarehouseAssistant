from datetime import datetime, date, timedelta
import pandas as pd

#file = pd.read_csv('../7.10/淘宝助理.csv',usecols=['title', 'cid'])
#file = pd.read_excel('../7.10/淘宝助理.xlsx',names=['宝贝名称','宝贝类目'])
file = pd.read_excel('../7.10/淘宝助理.xlsx',header=2)
print(file.loc[:,['放入仓库','商家编码']])
