from core.json import load_json
from core.constance import data_path, table_path, types

TEMPLATE = '''# %s
%s
| id | 中文 | 英文 | 日文 |
| --- | --- | --- | --- |
%s'''
POOL_TEXT = '\n**各服务器卡池id并不相同，非简中服id已用`_`前缀标出，详细请查看' \
            '[Kengxxiao/ArknightsGameData](https://github.com/Kengxxiao/ArknightsGameData)**  \n' \
            '常规轮换池以特殊ID `COMMON` 代替，不再展示重复数据\n'

for _type in types + ['all']:
    name = _type.lower()
    data = load_json(data_path % name)
    with open(table_path % name, mode='wt', encoding='utf-8') as f:
        f.write(TEMPLATE % (name[0].upper() + name[1:],
                            POOL_TEXT if _type == 'POOL' else '', '\n'.join(
            f'| {_id} | {langs.get("zh_CN", "-")} | {langs.get("en_US", "-")} | {langs.get("ja_JP", "-")} |'
            for _id, langs, in data.items()
        )))
