import os

cwd = os.getcwd()

base = os.path.join(cwd, 'ArknightsName')

resource_path = 'gamedata/%s/gamedata/'
excel_path = resource_path + 'excel/'

char_path = excel_path + 'character_table.json'
skin_path = excel_path + 'skin_table.json'
enemy_path = excel_path + 'enemy_handbook_table.json'
activate_path = excel_path + 'activity_table.json'
team_path = excel_path + 'handbook_team_table.json'
item_path = excel_path + 'item_table.json'
gacha_path = excel_path + 'gacha_table.json'  # tag & pool info
skill_path = excel_path + 'skill_table.json'
stage_path = excel_path + 'stage_table.json'
zone_path = excel_path + 'zone_table.json'

story_dir = resource_path + 'story'

types = [
    'OPERATOR',
    'TOKEN',
    'TRAP',
    'SKIN',
    'BRAND',
    'ENEMY',
    'ACTIVATE',
    'TEAM',
    'ITEM',
    'TAG',
    'POOL',
    'SKILL',
    'STAGE',
    'ZONE'
]

data_path = base + '/data/%s.json'
version_path = base + '/version/%s.txt'
table_path = base + '/table/%s.md'

for path in [
    data_path,
    version_path,
    table_path
]:
    if not os.path.exists(os.path.dirname(path)):
        os.mkdir(os.path.dirname(path))
