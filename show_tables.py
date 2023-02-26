from core.json import load_json
from core.constance import data_path, table_path, types

TEMPLATE = '''# %s

tip: 请善用浏览器的搜索功能

%s
| id | 中文 | English | 日文 |
| --- | --- | --- | --- |
%s'''
POOL_TEXT = '\n**各服务器卡池id并不相同，非简中服id已用`_`前缀标出，详细请查看' \
            '[Kengxxiao/ArknightsGameData](https://github.com/Kengxxiao/ArknightsGameData)**  \n' \
            '常规轮换池以特殊ID `COMMON` 代替，不再展示重复数据\n'

for _type in types:
    name = _type.lower()
    data = load_json(data_path % name)
    with open(table_path % name, mode='wt', encoding='utf-8') as f:
        f.write(TEMPLATE % (name[0].upper() + name[1:],
                            POOL_TEXT if _type == 'POOL' else '', '\n'.join(
            f'| {_id} | {langs.get("zh_CN", "-")} | {langs.get("en_US", "-")} | {langs.get("ja_JP", "-")} |'
            for _id, langs, in data.items()
        )))

name = 'all'
data = load_json(data_path % name)
with open(table_path % name, mode='wt', encoding='utf-8') as f:
    f.write(TEMPLATE % (name[0].upper() + name[1:], '', '\n'.join(
        f'| {_id} | {d["names"].get("zh_CN", "-")} | {d["names"].get("en_US", "-")} | {d["names"].get("ja_JP", "-")} |'
        for _id, d, in data.items()
    )))

name = 'npc'
data = load_json(data_path % name)
with open(table_path % name, mode='wt', encoding='utf-8') as f:
    f.write(TEMPLATE %
            (name[0].upper() + name[1:],
             '**如发现NPC名称数据有误，欢迎提交[Issue](https://github.com/Arkfans/ArknightsName/issues/new)**\n', ''))
    for npc, d in data.items():
        names = [d.get('zh_CN', []), d.get('en_US', []), d.get('ja_JP', [])]
        length = max(len(i) for i in names)
        for i in range(length):
            if i == 0:
                f.write(f'| {npc} |')
                for j in range(len(names)):
                    if i >= len(names[j]):
                        f.write(' - |')
                    else:
                        f.write(f' {names[j][i]} |')
            else:
                f.write(f'|   |')
                for j in range(len(names)):
                    if i >= len(names[j]):
                        f.write('   |')
                    else:
                        f.write(f' {names[j][i]} |')
            f.write('\n')
