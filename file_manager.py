import xlrd
import csv
import requests
import os

def get_svt_id_dic():
    '''从者ID: 游戏内编号'''
    return get_id_to_game_id('svts_jp.csv')


def get_cft_id_dic():
    '''从者ID: 游戏内编号'''
    return get_id_to_game_id('cfts_jp.csv')


def get_id_to_game_id(name):
    '''从者ID: 游戏内编号'''
    dic = {}
    with open(r'./decoded_files/{0}'.format(name), encoding='UTF-8-sig') as f:
        svts = list(csv.reader(f))
        for item in svts:
            dic[int(item[0])] = int(item[1])
    return dic


def get_file(name):
    '''项目根目录，文件名包含后缀名'''
    f = open(r'./{0}'.format(name), 'r', encoding='utf8')
    return f.read()


def download_all_svt_html():
    excel_file = xlrd.open_workbook(r'./decoded_files/fgo.wiki.xlsx')
    svt_sheet = excel_file.sheet_by_name('servant_list_raw')
    names = list(map(lambda x: x.replace('・', '·'), svt_sheet.col_values(5)[1:]))
    for i, name in enumerate(names):
        print(name)
        url = 'https://fgo.wiki/w/' + name
        if name == 'BeastⅢ/R':
            name = 'BeastⅢ_R'
        prefix = str(i+1).zfill(3) + '_'
        path = r'./servant_files/{0}{1}'.format(prefix, name) + ".html"
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(requests.get(url).content)
                print(str(i) + ': ' + name + '\n')