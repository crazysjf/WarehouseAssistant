import re

l = ['11032C-C008-卡其-XL',
'11032C-C008-雾蓝-M',
'11032C-C008-杏-s',
'11032C-C008-杏',
'11032C-C008-粉',
'11034-971-黄蓝条',
'11035-7356-白',
'11035-7356-粉',
'11035-7356-黑']


def split_code(s):
    i = s.rfind('-')
    return s[0:i]

for i in l:
    m = re.match(r'(.*)-[^-SMLXsmlx]+(-[SMLXsmlx]+)*$', i)
    if m != None:
        print(m.group(1))
#
#
# m = map(split_code, l)
# print(list(m))
# print(set(m))
#
# #