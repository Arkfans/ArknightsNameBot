__all__ = [
    'load_json',
    'dump_json'
]

import json


def load_json(path: str):
    with open(path, mode='rt', encoding='utf-8') as f:
        return json.load(f)


def dump_json(data, path: str, **kwargs):
    with open(path, mode='wb', encoding='utf-8') as f:
        json.dump(data, f, **kwargs)
