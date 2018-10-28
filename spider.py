from helper import *
from lxml import etree
from urllib import parse
import file_manager
import db
import os

CUR_ID = 6
CUR_SVT_ID = 6
CUR_UNIQUE_NAME = '齐格飞'

id_to_game_id_dic = file_manager.get_svt_id_dic()


def extract_basic_data(tree):
    global CUR_UNIQUE_NAME

    """基础数值"""
    def set_CUR_ID(s):
        global CUR_ID
        global CUR_SVT_ID
        global id_to_game_id_dic
        CUR_ID = int(s[0][3:-1])
        CUR_SVT_ID = id_to_game_id_dic[CUR_ID]
        return CUR_ID

    def extract_hits(tree):
        hits_table = tree[0]
        q_a = hits_table.xpath('tr[19]/td//text()')
        b_extra = hits_table.xpath('tr[20]/td//text()')
        np = hits_table.xpath('tr[21]/td//text()')
        q_a.extend(b_extra)
        q_a.extend(np)
        return list2str(q_a)

    def extract_chara_graph(div):
        urls = map(parse.unquote, div[0].xpath(TAB + '/p/a/img//@src'))
        titles = div[0].xpath(TAB + '//@title')
        ''' 下载灵基图片
        global CUR_ID
        for i, url in enumerate(urls):
            with open('./chara_graph/' + str(CUR_ID).zfill(3) + '_' + titles[i] + '.png', 'wb') as f:
                f.write(requests.get('https://fgo.wiki' + url).content)
                f.close()
        '''
        return ';'.join([list2str(titles), list2str(list(urls))])

    def extract(params):
        s = tree.xpath(params[0])
        if len(params) == 2:
            return params[1](s)
        elif len(s):
            return del_rt(s[0])

    '''[xpath路径, 提取文本的处理方法]'''
    basic_data_xpaths = [
        ['.', lambda x: 0],
        ['tr[3]/th/text()', set_CUR_ID],  # id 16
        ['tr[1]/th[2]/a/img/@alt', lambda x: x[0][0]],  # rarity 1
        ['.', lambda x: CUR_UNIQUE_NAME],
        ['tr[1]/th[1]//text()', combine_texts],  # cn_name 阿拉什
        ['tr[2]/td[1]//text()', combine_texts],  # jp_name アーラシュ
        ['tr[3]/td[1]//text()', combine_texts],  # en_name Arash
        ['tr[27]/td/text()'],  # nick_name 昵称
        ['tr[5]/td[1]/a/text()'],  # illustrator 画师
        ['tr[5]/td[2]/a/text()'],  # cv 声优
        ['tr[7]/td[1]/text()'],  # class 职阶
        ['tr[7]/td[2]/a/text()'],  # gender 性别
        ['tr[7]/td[3]/text()'],  # height 身高
        ['tr[7]/td[4]/text()'],  # weight 体重
        ['tr[7]/td[5]/a//text()', list2str],  # alignment 混沌,中庸
        ['tr[7]/td[6]/a/text()'],  # attribute 隐藏属性
        ['tr[9]/td[1]/text()'],  # strength 筋力
        ['tr[9]/td[2]/text()'],  # endurance 耐久
        ['tr[9]/td[3]/text()'],  # agility 敏捷
        ['tr[9]/td[4]/text()'],  # magic 魔力
        ['tr[9]/td[5]/text()'],  # lucky 幸运
        ['tr[9]/td[6]/text()'],  # np 宝具
        ['tr[10]/td/a/img//@alt', lambda x: ','.join(map(lambda y: del_rt(y)[:-4], x))],  # cards 配卡 Qucik,Arts,Arts,Buster,Buster
        ['tr[17]/td//text()', list2str],  # np_gain NP获得率
        ['.', extract_hits],  # hits
        ['tr[23]/td[1]/text()'],  # star_rate 出星率
        ['tr[23]/td[2]/text()'],  # death_rate 被即死率
        ['tr[23]/td[3]/text()'],  # star_weight 暴击星分配权重
        ['tr[25]/td[1]/a//text()', list2str],  # traits 特性
        ['tr[25]/td[2]/a/text()', lambda x: x[0] == '是'],  # human_like bool 人型
        ['tr[25]/td[3]/a/text()', lambda x: x[0] == '是'],  # ea_target bool 被EA特攻
        ['//div[starts-with(@id, "tabber")]', extract_chara_graph]  # chara_graph 灵基图集
    ]
    if tree.xpath('self::' + WIKITABLE):
        data = list(map(extract, basic_data_xpaths))
        global CUR_SVT_ID
        data[0] = CUR_SVT_ID
        return data


def extract_np_skill(tree, deal, isNP):
    datas = []
    global CUR_SVT_ID
    """宝具和持有技能"""
    # 普通table
    wikitable_node = tree.xpath('self::' + WIKITABLE)
    if wikitable_node:
        data = deal(wikitable_node[0])
        tag_condition_comment = ['', '', '']
        if isNP:
            np_id = CUR_SVT_ID + 1
            data[0] = np_id
            # 注释
            comment_node = tree.xpath('p[1]//text()')
            if comment_node:
                comment = combine_texts(comment_node[0])
                tag_condition_comment[2] = comment
        else:
            tag_condition_comment.pop(2)

        data.extend(tag_condition_comment)
        datas.append(data)
    else:
        # <div id="tabber-XXX"> 判断省略
        # 多条目table
        tabbertab_node = tree.xpath(TAB)
        if not tabbertab_node: return
        for tab in tabbertab_node:
            tag_condition_comment = ['', '', '']
            tag = tab.xpath('self::div/@title')[0]
            tag_condition_comment[0] = tag
            # 开放关卡
            open_mission_node = tab.xpath('p[1]/a//text()')
            # 有链接即为关卡
            if open_mission_node:
                open_mission = ','.join(open_mission_node)
            else:  # 无链接的关卡 eg 国服未开放的章节
                open_mission = tab.xpath('p/text()')[0]
            # 开放条件
            open_condtion_node = tab.xpath('p[1]/i/text()')
            if open_condtion_node:
                open_condtion = open_condtion_node[0]
                tag_condition_comment[1] = ','.join([open_mission, open_condtion])
            if isNP:
                # 注释 宝具项才可能含有注释
                comment_node = tab.xpath('p[2]//text()')
                if comment_node:
                    comment = combine_texts(comment_node[0])
                    tag_condition_comment[2] = comment
            else:
                tag_condition_comment.pop(2)
            # table
            wikitable_node = tab.xpath(WIKITABLE)
            if wikitable_node:
                data = deal(wikitable_node[0])
                if data:
                    if isNP:
                        num = 2 if tag == '强化后' else 1
                        np_id = CUR_SVT_ID + num
                        data[0] = np_id
                    data.extend(tag_condition_comment)
                    datas.append(data)
    return datas


def extract_effect(tree):
    """2行一组的效果、效果数值"""
    effect_trs = tree.xpath('tr')
    # 宝具效果描述起于第2行，2行一组
    effect_trs_count = int((len(effect_trs) - 1) / 2)
    effect_list = []
    effect_values_list = []
    special_attack_set = set()
    for i in range(effect_trs_count):
        # 特攻
        special_attack_target_node = effect_trs[i * 2 + 1].xpath('th/span/a//text()')
        if special_attack_target_node:
            special_attack_set = set(map(lambda s: s[1: -1], special_attack_target_node))

        # 宝具效果
        effect = combine_texts(effect_trs[i * 2 + 1].xpath('th//text()'))
        # 宝具数值
        effect_values = list(map(del_rt, filter(lambda x: x != '\n', effect_trs[i * 2 + 2].xpath('td//text()'))))
        effect_list.append(effect)
        effect_values_list.append(effect_values)
    return [special_attack_set, effect_list, effect_values_list]


def extract_noble_phantasm(tree):
    """宝具"""
    # 指令卡
    command_card = tree.xpath('tr[1]/th[1]/div/div/a/img/@alt')[0][:-4]
    # 等级
    level = del_rt(tree.xpath('tr[1]/th[1]/p[1]/text()')[0])
    # 种类
    target_type = del_rt(tree.xpath('tr[1]/th[1]/p[2]/text()')[0])
    # 依次是 日文名 英文名 中文名
    names = list(filter(lambda x: not x.startswith('\n'), tree.xpath('tr[1]/th[2]//text()')))
    if len(names) == 1:
        names = ['', '', names[0]]
    effects = extract_effect(tree)
    global CUR_ID
    data = [0, CUR_ID, names[2], names[0], names[1], command_card, level, target_type]
    data.extend(effects)
    return data

def extract_owned_skill(tree):

    # 技能图标url
    img_name = parse.unquote(tree.xpath('tr[1]/th[1]/a/img/@alt')[0])[:-4]
    # 技能名称
    name = combine_texts(tree.xpath('tr[1]/th[2]//text()'))
    # 充能时间
    charge_time = tree.xpath('tr[1]/th[3]/text()')[0][:-1]
    effects = extract_effect(tree)
    global CUR_ID
    data = [CUR_ID, name, img_name, charge_time]
    data.extend(effects)
    return data


def extract_class_skill_name(tree):
    wikitable_node = tree.xpath('self::' + WIKITABLE)
    if not wikitable_node: return
    wikitable = wikitable_node[0]
    trs = wikitable.xpath('tr')
    count = int(len(trs)/2)
    data = []
    for i in range(count):
        tr = trs[2*i]
        name = del_rt(tr.xpath('th[2]/text()')[0])
        level = del_rt(tr.xpath('td/text()')[0]).replace('固有等级：', '')
        name = name + ' ' + level.replace(' ', '')
        data.append(name)
    return data


def extract_material(tree):
    """提取素材需求（包括 灵基再临、技能强化）"""
    wikitable_node = tree.xpath('self::' + WIKITABLE)
    if not wikitable_node: return
    wikitable = wikitable_node[0]
    trs = wikitable.xpath('tr')
    materials = []
    # td_count = len(trs[0].xpath('td'))
    # for td_index in range(0, td_count):
    #     for i, tr in enumerate(trs):
    #         grid_node = tr.xpath('td')
    #         if grid_node:
    #             grid = grid_node[td_index]
    #             # 技能强化第一个会多一个td包住div
    #             names = grid.xpath('descendant-or-self::div//a/@title')
    #             names.append('QP')
    #             nums = grid.xpath('descendant-or-self::div//span/text()')
    #             materials.append([names, nums])
    #     if i == len(trs) and td_index == td_count - 1:
    #         break

    for tr in trs:
        tds = tr.xpath('td')
        if tds:
            for td in tds:
                names = td.xpath('descendant-or-self::div//a/@title')
                names.append('QP')
                nums = td.xpath('descendant-or-self::div//span/text()')
                materials.append([names, nums])
    materials.sort(key=lambda x: float(x[1][-1][:-1]))
    return materials


def extract_bond_story(tree):
    """羁绊故事"""
    bond_story_tabbertab = tree.xpath('self::' + TABBER_TAB)
    if not bond_story_tabbertab:
        return
    bond_storys = []
    for tab in bond_story_tabbertab:
        tag = tab.xpath('@title')[0]
        content_table = tab.xpath('table')[0]
        # 解锁条件：通关「屠龙者」后开放  未包含屠龙者链接
        title = combine_texts(content_table.xpath('tr[1]/th//text()'))
        content = reduce(add, content_table.xpath('tr[2]/td/div/p//text()'))
        if content[-1] == '\n':
            content = content[:-1]
            bond_storys.append([tag, title, content])
    return bond_storys


def extract_bond_point(tree):
    """羁绊点数"""
    wikitable_node = tree.xpath('self::div[@class="nomobile"]/table')
    if not wikitable_node: return
    wikitable = wikitable_node[0]
    points = list(map(del_rt, wikitable.xpath('tr[2]/td//text()')))
    point_cumulation = list(map(del_rt, wikitable.xpath('tr[3]/td//text()')))
    rewards = wikitable.xpath('tr[4]/td//text()')
    reward_imgs = wikitable.xpath('tr[4]/td/div/a//@href')
    reward_nums = wikitable.xpath('tr[4]/td/div/span//text()')
    for i, r in enumerate(reward_imgs):
        if r.endswith('%E5%9C%A3%E6%99%B6%E7%9F%B3.png'):
            reward_imgs[i] = '圣晶石x' + reward_nums[i]
        elif r.endswith('%E9%BB%84%E9%87%91%E6%9E%9C%E5%AE%9E(%E6%97%A0%E6%A1%86).png'):
            reward_imgs[i] = '黄金果实x' + reward_nums[i]
    reward_imgs.append('羁绊礼装')
    rest = 10 - len(reward_imgs)
    reward_list = ['-' for i in range(0, rest)]
    reward_list.extend(reward_imgs)
    return [points, point_cumulation, reward_list]


def extract_related_craft_essence(tree):
    """相关礼装"""
    tabbertab_node = tree.xpath('self::' + TABBER_TAB)
    if not tabbertab_node: return
    tags = list(map(lambda x: x.xpath('@title')[0], tabbertab_node))
    names = list(map(lambda x: del_rt(x.xpath('table[1]/tr[1]/th/text()')[0]), tabbertab_node))
    return [tags, names]


def extract_voice_text(tree):
    """语音文本"""
    wikitable_node = tree.xpath('self::table[starts-with(@class, "wikitable nomobile")]')
    if not wikitable_node: return
    wikitable = wikitable_node[0]
    tag = wikitable.xpath('tr[1]/th/b/text()')[0]
    trs = wikitable.xpath('tr')[1:]
    titles = []
    contents = []
    for tr in trs:
        titles.append(tr.xpath('th/b/text()')[0])
        contents.append(combine_texts(tr.xpath('td/p//text()')))
    return [tag, titles, contents]


def extract_voice_related_svt(tree):
    """语音关联从者"""
    wikitable_node = tree.xpath('self::table')
    if not wikitable_node: return
    wikitable = wikitable_node[0]
    return list(map(lambda x: x[:-4], wikitable.xpath('tr/td/a/img//@alt')))


def extract_avatar(tree):
    """头像 战斗形象"""
    wikitable_node = tree.xpath('self::table[@class="wikitable"]')
    if not wikitable_node: return
    wikitable = wikitable_node[0]
    trs = wikitable.xpath('tr')
    if len(trs) < 3:
        img_urls = trs[0].xpath('th//a/img/@src')
        titles = list(map(del_rt, trs[1].xpath('td//text()')))
    else:
        img_urls = list(map(lambda x: x.xpath('td/a/img//@src'), trs[:-1]))
        titles = list(map(del_rt, trs[-1].xpath('td//text()')))
    return [img_urls, titles]


def extract_pickup(tree):
    """Pick up 下载的网页暂时无法使用"""
    tabbertab_node = tree.xpath('self::' + TABBER_TAB)
    if not tabbertab_node: return
    tags = list(map(lambda x: x.xpath('@title')[0], tabbertab_node))
    imgs = list(map(lambda x: x.xpath('div[1]/div/div/div/a/img/@src')[0], tabbertab_node))
    names = list(map(lambda x: reduce(add, x.xpath('div[1]/div/div/div/div/center//text()')), tabbertab_node))
    return [tags, imgs, names]


# -------------------------------------------------------------------------------------------------------------------- #

def extract_class_skill(tree):
    """抓一下 https://fgo.wiki/w/技能一览/职阶技能"""
    name = del_rt(tree.xpath('tr[1]/th[1]/text()')[0])
    level = del_rt(tree.xpath('tr[1]/td/text()')[0])
    img_name = del_rt(tree.xpath('tr[2]/th[1]/a/img/@alt')[0])[:-4]
    trs = tree.xpath('tr')[1:-2]
    effects = [combine_texts(trs[0].xpath('th[2]//text()'))]
    effect_values = [del_rt(trs[0].xpath('td/text()')[0])]

    if len(trs) > 1:
        adjusted_trs = trs[1:]
        effects.extend(list(map(lambda x: combine_texts(x.xpath('th//text()')), adjusted_trs)))
        effect_values.extend(list(map(lambda x: del_rt(x.xpath('td/text()')[0]), adjusted_trs)))
    return[name, img_name, effects, effect_values]


def prepare_class_skill(tree):
    wikitable_node = tree.xpath('self::table[@class="wikitable"]')
    datas = []
    if wikitable_node:
        wikitable = wikitable_node[0]
        datas.append(extract_class_skill(wikitable))
    else:
        tabbertab_node = tree.xpath('self::div[starts-with(@id, "tabber-")]/div[@class="tabbertab"]')
        if not tabbertab_node: return
        # tags = list(map(lambda x: x.xpath('@title')[0], tabbertab_node))
        datas.extend(map(lambda x: extract_class_skill(x.xpath('table[@class="wikitable"]')[0]), tabbertab_node))
    return datas


db.exec_sql(db.create_sqls['basic_data'])


def extract_s(html):
    cur_tag = '基础数值'
    cur_child_tag = ''

    tree = etree.HTML(html)
    tree_start_base = tree.xpath('''//*[@id="mw-content-text"]/div/h2/span[text()="基础数值"]/../following-sibling::*''')
    for node in tree_start_base:

        child_tag_node = node.xpath('self::h3/span[1]/text()')
        if child_tag_node:
            cur_child_tag = child_tag_node[0]

        tag_node = node.xpath('self::h2/span[1]/text()')
        if tag_node:
            cur_tag = tag_node[0]

        if cur_tag == '基础数值':
            data = extract_basic_data(node)
            if data:
                print(data)
                db.exec_sql(db.insert_sqls['basic_data'], data)
                cur_tag = ''
        elif cur_tag == '宝具':

            datas = extract_np_skill(node, extract_noble_phantasm, True)
            if datas:
                print(datas)
            # if datas:
            #     for data in datas:
            #         fgo_db.insert_noble_phantasm([
            #             data[0],
            #             data[1],
            #             data[2],
            #             data[3],
            #             data[4],
            #             data[5],
            #             data[6],
            #             data[7],
            #             data[8],
            #             ','.join(data[9]),
            #             ','.join(data[10]),
            #             ';'.join(map(lambda x: ','.join(x), data[11])),
            #             data[12],
            #             data[13],
            #         ])

        elif cur_tag == '技能':
            if cur_child_tag == '持有技能':
                pass
                datas = extract_np_skill(node, extract_owned_skill, False)
                if datas:
                    print(datas)
                # if datas:
                #     for data in datas:
                #         fgo_db.insert_skill([
                #             data[0],
                #             data[1],
                #             data[2],
                #             data[3],
                #             data[4],
                #             data[5],
                #             ','.join(data[6]),
                #             ','.join(data[7]),
                #             ';'.join(map(lambda x: ','.join(x), data[8])),
                #             data[9],
                #             data[10],
                #         ])
            if cur_child_tag == '职阶技能':
                pass
        elif cur_tag == '素材需求':
            pass
            # datas = extract_material(node)
            # if datas:
            #     global CUR_ID
            #     for data in datas:
            #         fgo_db.insert_material([
            #             0,
            #             0,
            #             CUR_ID,
            #             ','.join(data[0]),
            #             ','.join(data[1]),
            #             cur_child_tag
            #         ])

        # elif cur_tag == '从者羁绊':
        #     if cur_child_tag == '羁绊故事':
        #         print(extract_bond_story(node))
        #     elif cur_child_tag == '羁绊点数':
        #         print(extract_bond_point(node))
        # elif cur_tag == "相关礼装":
        #     print(extract_related_craft_essence(node))
        # elif cur_tag == "语音文本":
        #     print(extract_voice_text(node))
        # elif cur_tag == "语音关联从者":
        #     print(extract_voice_related_svt(node))
        # elif cur_tag == "各阶段头像与战斗形象":
        #     print(extract_avatar(node))



files = os.listdir('./servant_files')
files.sort(key=lambda x: x[:3])
for file in files[1:]:
    id = int(file[:3])

    CUR_UNIQUE_NAME = file[4:-5]
    if file in ['168_BeastⅢ/R.html', '083_所罗门.html', '151_盖提亚.html', '149_提亚马特.html',
                '152_所罗门(Caster).html']:
        continue
    print(id)
    path = os.getcwd() + '/servant_files/' + file
    f = open(path, 'r', encoding='utf8')
    html = f.read()
    extract_s(html)

db.save()

