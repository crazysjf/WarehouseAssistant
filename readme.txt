
# 使用方法

goods_file:普通商品资料导出文件
sales_file:报表=>商品主题分析导出文件
stock_file:库存=>箱及仓位库存导出文件


从淘宝助理导出的文件在Excel中打开，去掉1，2行，仅保留“放入仓库”和“商家编码”即可，存储为“淘宝助理.xlsx”

从淘宝助理导出所有宝贝信息非常慢，需要1-2个小时。


# 开发相关
## 基本思路
导出几个固定的excel，自动分析。
excel转成pandas dataframe，直接分析或者转成sqlite table后用sql分析。
结果转成pandas之后再转成excel导出。

SQlite And pandas：https://www.dataquest.io/blog/python-pandas-databases/
Join And Merge Pandas Dataframe：https://chrisalbon.com/python/data_wrangling/pandas_join_merge_dataframe/

## 判断标准

#### 半价清仓
上架超过30天，所有SKU的7天销量合计低于2件的宝贝，以款为单位，不是以SKU为单位。

19.6.25之前为0件。清仓判断需要更严格。


#### 销量过低SKU
上架超过30天，周销<=2，15天销量<=5，且不包括在清仓处理中 的SKU

### 可下架商品
清仓已经15天且无15天内无销量的款，此处仅选出清仓且15天销量为0的款，具体清了多少时间要选出后在筛选


## TODO
### 20190625
 - 清仓导入报表，销低导入报表的备注日期里面要加入年份。6.14 -> 19.6.14，以免和去年重复

### 以前

 - 清仓判断：本身备注有清字的不纳入清仓范围
 - 下架判断：清仓1周以上，整个款都没有销量的，做下架处理


