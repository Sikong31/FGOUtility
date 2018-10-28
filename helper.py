from functools import reduce


WIKITABLE = 'table[starts-with(@class, "wikitable nomobile")]'
TABBER_TAB = 'div[starts-with(@id, "tabber-")]/div[@class="tabbertab"]'
TAB = 'div[@class="tabbertab"]'


def add(x, y):
    return x + y


def del_rt(s):
    """替换换行符"""
    if isinstance(s, str):
        return s.replace('\n', '')
    return s


def combine_texts(texts):
    """字符串数组合并成一个字符串(删除最后的换行)"""
    if isinstance(texts, list):
        line = reduce(add, texts)
        if line.endswith('\n'):
            line = line[:-1]
        return line
    return texts


def list2str(texts):
    if isinstance(texts, list):
        return ','.join(map(del_rt, texts))
    return texts