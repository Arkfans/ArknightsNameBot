import re

from .json import *
from .constance import *
from .data import Manager


class Parser:
    remove_pool_prefix = re.compile(r'([^_]+_)(?:.+_)(\d+_\d+_\d+)').sub
    continue_stage_prefix = re.compile(r'^(easy|tough)|((tm|ex|fin)\d{2}|#f#|_ex)$')

    def __init__(self, lang: str):
        self.lang: str = lang
        self.parse()

    def parse(self):
        self.parse_char(load_json(char_path % self.lang))
        skin_data = load_json(skin_path % self.lang)
        self.parse_by_key({k: {'name': v['displaySkin']['skinName']} for k, v in skin_data['charSkins'].items()
                           if v['displaySkin']['skinName']}, 'SKIN')
        self.parse_by_key(skin_data['brandList'], 'BRAND', 'brandName')
        self.parse_by_key(load_json(enemy_path % self.lang), 'ENEMY')
        self.parse_by_key(load_json(activate_path % self.lang)['basicInfo'], 'ACTIVITY')
        self.parse_by_key(load_json(team_path % self.lang), 'TEAM', 'powerName')
        self.parse_by_key(load_json(item_path % self.lang)['items'], 'ITEM')
        gacha_data = load_json(gacha_path % self.lang)
        self.parse_by_key2(gacha_data['gachaTags'], 'TAG', 'tagId', 'tagName')
        self.parse_pool(gacha_data['gachaPoolClient'])
        self.parse_by_key({k: v['levels'][0] for k, v in load_json(skill_path % self.lang).items()}, 'SKILL')
        self.parse_by_key({k: v for k, v in load_json(stage_path % self.lang)['stages'].items()
                           if not self.continue_stage_prefix.search(k) and v['name']}, 'STAGE')
        self.parse_by_key({k: v for k, v in load_json(zone_path % self.lang)['zones'].items()
                           if v['zoneNameSecond']}, 'ZONE', 'zoneNameSecond')

    def parse_by_key(self, data: dict, _type: str, key: str = 'name'):
        try:
            for _id, data in data.items():
                Manager.single(_id, _type).add_name(self.lang, data[key])
        except Exception as e:
            print('[ERROR]', data)
            raise e

    def parse_by_key2(self, data: list, _type: str, key1: str, key2: str):
        try:
            for data in data:
                Manager.single(data[key1], _type).add_name(self.lang, data[key2])
        except Exception as e:
            print('[ERROR]', data)
            raise e

    def parse_char(self, data: dict):
        for char_id, data in data.items():
            if data['profession'] == 'TOKEN':
                char = Manager.single(char_id, 'TOKEN')
            elif data['profession'] == 'TRAP':
                char = Manager.single(char_id, 'TRAP')
            else:
                char = Manager.single(char_id, 'OPERATOR')
            char.add_name(self.lang, data['name'])

    def parse_pool(self, data: list):
        for pool in data:

            _id = self.remove_pool_prefix(r'_\1\2', pool['gachaPoolId'])
            if _id.endswith('NORM_0_1_1'):
                Manager.single('COMMON', 'POOL').add_name(self.lang, pool['gachaPoolName'])
            else:
                Manager.single(_id, 'POOL').add_name(self.lang, pool['gachaPoolName'])

        common = set(i for i in Manager.single('COMMON', 'POOL').names.values())
        for _id, data in Manager._single['POOL'].copy().items():
            if _id == 'COMMON':
                continue
            for value in data.names.values():
                if value in common:
                    Manager._single['POOL'].pop(_id)
                    continue
