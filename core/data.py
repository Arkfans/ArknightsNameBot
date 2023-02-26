import os
import json
import hashlib
from typing import Dict, List, Tuple, Set

from .constance import types, data_path, version_path


class Single:
    """
    单语种名字item，如 角色/敌人/材料
    """

    def __init__(self, _id: str, _type: str):
        self.id: str = _id
        self.type: str = _type
        self.names: Dict[str, str] = {}

    def add_name(self, lang: str, name: str):
        self.names[lang] = name

    def __repr__(self):
        return f'[{self.type}:{self.id}:{self.names}]'

    @property
    def data(self):
        return dict(sorted(self.names.items(), key=lambda x: x[0]))


class NPC:
    """
    单语种可能对应多名
    """

    def __init__(self, _id: str):
        self.id: str = _id
        self.names: Dict[str, List[str]] = {}
        self.name_set: Set[str] = set()

    def add_name(self, lang: str, name: str):
        if lang in self.names:
            if name not in self.names[lang]:
                self.names[lang].append(name)
        else:
            self.names[lang] = [name]

    @property
    def data(self):
        return dict(sorted({i[0]: sorted(i[1]) for i in self.names.items()}.items(), key=lambda x: x[0]))

    def __repr__(self):
        return f'[NPC:{self.id}:{self.names}]'


class TypeManager(dict):
    @property
    def data(self):
        return {k: v.data for k, v in sorted(self.items(), key=lambda x: x[0])}


class Manager:
    def __init__(self):
        self._single: Dict[str, Dict[str:Single]] = {i: TypeManager() for i in types}
        self._npc: Dict[str, NPC] = {}

    def single(self, _id: str, _type: str) -> Single:
        if _id not in self._single[_type]:
            self._single[_type][_id] = Single(_id, _type)
        return self._single[_type][_id]

    def npc(self, _id: str) -> NPC:
        if _id not in self._npc:
            self._npc[_id] = NPC(_id)
        return self._npc[_id]

    def save(self):
        r1 = self.save_common()
        r2 = self.save_npc()
        if r1[0] or r2[0]:
            _hash = hashlib.md5((r1[1] + r2[1]).encode('utf-8')).hexdigest()
            os.system('echo "update=1" >> $GITHUB_ENV')
            os.system(f'echo "version={_hash[:7]}" >> $GITHUB_ENV')
        else:
            print('nothing updated')
            os.system('echo "update=0" >> $GITHUB_ENV')

    def save_common(self) -> Tuple[bool, str]:
        update = False
        all_data = {}
        for _type, type_manager in self._single.items():
            data = type_manager.data
            all_data.update({k: {'type': _type, 'names': v} for k, v in data.items()})
            _type = _type.lower()
            _hash = hashlib.md5(json.dumps(data, ensure_ascii=False).encode('utf-8')).hexdigest()
            if os.path.exists(version_path % _type):
                with open(version_path % _type, mode='rt', encoding='utf-8') as f:
                    if f.read() == _hash:
                        continue
            update = True
            print(f'update {_type} {_hash}')
            with open(version_path % _type, mode='wt', encoding='utf-8') as f:
                f.write(_hash)
            with open(data_path % _type, mode='wt', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)

        _hash = hashlib.md5(
            json.dumps(dict(sorted(all_data.items(), key=lambda x: str(x[0]))), ensure_ascii=False).encode(
                'utf-8')).hexdigest()
        if not update:
            return False, _hash

        print(f'update all {_hash}')
        with open(version_path % 'all', mode='wt', encoding='utf-8') as f:
            f.write(_hash)
        with open(data_path % 'all', mode='wt', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False)

        return True, _hash

    def save_npc(self) -> Tuple[bool, str]:
        _type = 'npc'
        data = {k: v.data for k, v in sorted(self._npc.items(), key=lambda x: x[0])}
        _hash = hashlib.md5(json.dumps(data, ensure_ascii=False).encode('utf-8')).hexdigest()
        if os.path.exists(version_path % _type):
            with open(version_path % _type, mode='rt', encoding='utf-8') as f:
                if f.read() == _hash:
                    return False, _hash

        print(f'update {_type} {_hash}')
        with open(version_path % _type, mode='wt', encoding='utf-8') as f:
            f.write(_hash)
        with open(data_path % _type, mode='wt', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

        return True, _hash


Manager = Manager()
