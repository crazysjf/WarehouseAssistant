# -*- coding: utf-8 -*-

import os
import re

FILE_DIR = None  # 半常量


def set_file_dir(dir):
    global  FILE_DIR
    FILE_DIR = dir


def get_source_files():
    '''
    在dir里面找到3个xlsx文件并返回路径
    :param dir: 
    :return: (商品资料文件, 销量文件, 库存文件, 淘宝助理导出文件)。如果失败返回None
    '''
    if FILE_DIR == None:
        print("路径未设定")
        return None

    goods_file = None
    sales_file = None
    stock_file = None
    tb_assistant_file = None

    fs = os.listdir(FILE_DIR)
    for f in fs:
        m = re.match('商品资料.*\.xlsx$', f)
        if m != None:
            goods_file = f

        m = re.match('商品综合分析.*\.xlsx$', f)
        if m != None:
            sales_file = f

        m = re.match('箱及仓位库存.*\.xlsx$', f)
        if m != None:
            stock_file = f

        m = re.match('淘宝助理.*\.xlsx$', f)
        if m != None:
            tb_assistant_file = f


    r =  (goods_file, sales_file, stock_file, tb_assistant_file)
    r = list(map(lambda f: os.path.join(FILE_DIR, f) if f != None else None,r))
    file_meaning = ("商品文件", "销量文件", "库存问价", "淘宝助理导出文件")
    for i, f in enumerate(r):
        if f == None:
            print("找不到%s" % file_meaning[i])
    return r


def get_full_file_path(f):
    if FILE_DIR == None:
        print("路径未设定")
        return None
    return os.path.join(FILE_DIR, f)

def get_db_file():
    return get_full_file_path("db.sqlite")

def get_output_full_file_path(f):
    d = os.path.join(FILE_DIR, "结果")
    if not os.path.exists(d):
        os.makedirs(d)
    return get_full_file_path(os.path.join("结果", f))

if __name__ == "__main__":
    # set_file_dir("./6.20")
    # print(getDBFile())
    # print(getFiles())
    a = (1,2,3)
    m = map(lambda x: x+1, a)
    for i in m:
        print(i)
    print(list(m))