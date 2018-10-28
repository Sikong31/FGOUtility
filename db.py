import sqlite3

conn = sqlite3.connect(r'./db_files/servants.db')


def repeat(s, count):
    return ','.join([s for _ in range(count)])


create_sqls = dict(basic_data='''
    CREATE TABLE IF NOT EXISTS servant_basic_data (
        svt_id                  SMALLINT PRIMARY KEY,  -- 从者
        id                      SMALLINT,     -- id, 如 齐格飞 6
        rarity                  TINYINT,      -- 稀有度 1～5
        unique_name             VARCHAR(20),  -- 唯一的名称，如 '贞德・Alter·Santa·Lily'
        cn_name                 VARCHAR(20),  -- 中文名
        jp_name                 VARCHAR(20),  -- 日文名
        en_name                 VARCHAR(20),  -- 英文名
        nick_name               VARCHAR(20),  -- 昵称
        illustrator             VARCHAR(20),  -- 画师
        cv                      VARCHAR(20),  -- 声优
        class                   VARCHAR(20),  -- 职阶
        gender                  CHAR(4),      -- 性别
        height                  VARCHAR(10),  -- 身高 '154cm'
        weight                  VARCHAR(10),  -- 体重 '42kg'
        alignment               VARCHAR(20),  -- 属性，'中立,恶'
        attribute               VARCHAR(10),  -- 隐藏属性，'星'
        strength                VARCHAR(10),  -- 筋力 'A'
        endurance               VARCHAR(10),  -- 耐久 'B'
        agility                 VARCHAR(10),  -- 敏捷 'B'
        magic                   VARCHAR(10),  -- 魔力 'A+'
        lucky                   VARCHAR(10),  -- 幸运 'C'
        noble_phantasm          VARCHAR(10),  -- 宝具 'A++'
        cards                   VARCHAR(40),  -- 配卡 'Quick,Quick,Arts,Buster,Buster'
        np_gains                VARCHAR(40),  -- NP获得率 '1.07%,1.07%,1.07%,1.07%,1.07%,5%'
        hits                    VARCHAR(100), -- Hit信息  '3 Hits (16,33,51),2 Hits (33,67),4 Hits (10,20,30,40),...'
        star_rate               VARCHAR(6),   -- 出星率 '5.0%'
        death_rate              VARCHAR(6),   -- 被即死率 '37.3%'
        star_weight             smallint,     -- 暴击星分配权重 '9'
        traits                  VARCHAR(100), -- 特性 '龙,阿尔托莉雅脸,亚瑟,王'
        human_like              bit,          -- 人型 '1'
        ea_target               bit,          -- 被EA特攻 '0'
        chara_graph_urls        VARCHAR(400)  -- '初始状态～灵基再临III,灵基再临Ⅳ; /xxx/xxx.png, /xxx/xx.png'
    )
    ''', noble_phantasm='''
    CREATE TABLE IF NOT EXISTS servant_noble_phantasm (
        np_id                   SMALLINT PRIMARY KEY,  -- svt_id + 强化 ? 2 : 1 如齐格飞 100801(强化前) 100802(强化后)
        id                      SMALLINT,     -- id, 如 齐格飞 6
        cn_name                 VARCHAR(20),  -- 宝具中文名 '黑龙双克胜利剑'
        jp_name                 VARCHAR(20),  -- 宝具日文名 '黒竜双剋勝利剣'
        en_name                 VARCHAR(20),  -- 宝具英文名 'Cross Calibur'
        command_card            VARCHAR(20),  -- 宝具指令卡 'Quick'
        level                   VARCHAR(10),  -- 宝具等级 'A+'
        target_type             VARCHAR(40),  -- 宝具类型 '对人宝具'
        special_attack_target   VARCHAR(40),  -- 宝具特攻 'Saber职阶从者'
        effect_names            VARCHAR(200), -- 宝具效果 '对敌方单体发动超强大的攻击<宝具升级效果提升>, 对〔Saber职阶从者〕特攻<Over Charge时特效威力提升>'
        effect_values           VARCHAR(200), -- 宝具效果数值 '1200%	,1600%,1800%,1900%,2000%; 150%,162.5%,175%,187.5%,200%'
        tag                     VARCHAR(20),  -- '强化前'
        enhancement_condition   VARCHAR(60),  -- '强化关卡, 开放条件'
        comment                 VARCHAR(100)  -- 可能有的注释 如土方岁三
    )
    ''', skill='''
    CREATE TABLE IF NOT EXISTS servant_skill (
        skill_id                INTEGER PRIMARY KEY AUTOINCREMENT,  -- 无法获取日服数据,此键使用自增
        id                      SMALLINT,  -- id, 如 齐格飞 6
        name                    VARCHAR(30),
        img_name                VARCHAR(20),
        charge_time             VARCHAR(20),
        special_attack_target   VARCHAR(40),
        effect_names            VARCHAR(200),
        effect_values           VARCHAR(200),
        tag                     VARCHAR(20),
        enhancement_condition   VARCHAR(60)   -- '强化关卡, 开放条件' 如 '强化关卡 齐格飞2,（开放条件：灵基再临第4阶段。开放时间：从者强化活动 第6弹。'
    )
    ''', material='''
    CREATE TABLE IF NOT EXISTS servant_material (
        material_id            SMALLINT,  -- svt_id + 灵基再临（从者进化）,技能强化 ? 2 : 1
        id                     SMALLINT,  -- id, 如 齐格飞 6
        names                  VARCHAR(200),
        nums                   VARCHAR(200),
        tag                    VARCHAR(20)  -- '灵基再临（从者进化）' 或者 '技能强化'
    )
    ''')


insert_sqls = dict(
    basic_data='REPLACE INTO servant_basic_data VALUES ({0})'.format(repeat('?', 43-12+1)),
    noble_phantasm='REPLACE INTO servant_noble_phantasm VALUES ({0})'.format(repeat('?', 60-47+1)),
    skill='REPLACE INTO servant_skill (id, skill_index, name, img_name, charge_time, special_attack_target, effect_names, effect_values, tag, comment) VALUES ({0})'.format(repeat('?', 73-64)),
    material='REPLACE INTO servant_material VALUES ({0})'.format(repeat('?', 81-77+1))
)


def exec_sql(sql, values=''):
    if not len(values):
        conn.execute(sql)
    conn.execute(sql, tuple(values))


def save():
    conn.commit()
    conn.close()


print(insert_sqls['noble_phantasm'])

