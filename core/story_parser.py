import os
import re
import asyncio
import traceback
from typing import List, Dict, Set, Tuple, Optional, Union

import aiofiles

from core.data import Manager, NPC


class TypeHint:
    Params = Dict[str, Union[str, int, float]]


IgnoreLino = {
    # 由于某些特殊文本并不遵从Character name对应原则，在此忽略
    'level_main_06-12_end.txt': {305},
    'level_main_04-10_end.txt': {130},
    'level_main_03-05_end.txt': {41},
    'level_st_06-03.txt': {421},
    'level_main_04-02_beg.txt': {164}
}


class StoryParser:
    def __init__(self, lang: str, path: str):
        self.lang: str = lang
        self.path: str = path
        self.lino: int = 0
        self.ignore: Set[int] = IgnoreLino.get(os.path.split(self.path)[-1], set())
        self.curr_char: Optional[NPC] = None
        # 是否处于图片播放，当处于图片播放，name与curr_char可能不对应
        self.during_img: bool = False
        self.default: dict = {
            'fadetime': 0,
            'duration': 0,
            'x': 0,
            'y': 0,
            'a': 0,
            'r': 0,
            'g': 0,
            'b': 0
        }
        self.COMMON_NAME = {
            '？？？',
            '???'
        }

    async def parse(self):
        async with aiofiles.open(self.path, mode='rt', encoding='utf-8') as f:
            async for line in f:
                self.lino += 1
                if self.lino in self.ignore:
                    # 忽略非标准行
                    continue
                try:
                    self.parse_line(line.strip())
                except Exception:
                    print(traceback.format_exc())
                    print(self.path, self.lino, line)
                    raise KeyboardInterrupt

    def parse_line(self, text: str):
        if text.startswith('['):
            if text.endswith(']]'):
                # ?
                text = text[:-1]
            if text.endswith(')]='):
                # ?
                text = text[:-1]
            if text.endswith(')]'):
                # 功能函数
                self.parse_function(text)
            elif text.startswith('[name'):
                # 明确指向对话
                self.parse_chat(text)
            elif text.endswith(']'):
                # 处理空函数
                self.parse_empty_function(text)

    def parse_chat(self, text: str):
        if '"]' in text:
            index = text.index('"]')
        else:
            index = text.index('",')
        name = text[7:index].strip()
        if name in self.COMMON_NAME:
            return
        # chat = text[index + 2:].strip()
        if not self.curr_char:
            return
        if self.during_img:
            return

        self.curr_char.add_name(self.lang, name)

    def parse_function(self, text: str):
        index = text.find('(')
        # 忽略大小写 [自由の角]
        _type = text[1:index].lower()
        raw_params: List[Tuple[str, str]] = re.findall(r'(.+?)=(.*?), ?', text[index + 1:-2] + ',')
        params: TypeHint.Params = {}
        for key, value in raw_params:
            key = key.strip()
            value = value.strip()
            if value == '':
                params[key] = self.default[key]
            elif value == 'true':
                params[key] = True
            elif value == 'false':
                params[key] = False
            elif value.startswith('"'):
                params[key] = value.strip('"')
            elif '.' in value:
                params[key] = float(value)
            else:
                params[key] = int(value)

        if _type == 'character' or _type == 'charactercutin':
            # CharacterCutin 裁分式插入，格式类似于Character
            self.handle_character(params)
        elif _type == 'image':
            self.handle_image(params)
        elif _type == 'predicate':
            # 选项多分支
            self.curr_char = None
        elif _type == 'blocker':
            # 遮罩，可能会遗漏部分名称（未发现实例）
            self.curr_char = None

    def parse_empty_function(self, text: str):
        _type = text[1:-1].lower()
        if _type in [
            'character',  # 取消focus
            'dialog'  # 对话结束标识
        ]:
            self.curr_char = None
        elif _type == 'image':
            self.handle_image({'fadetime': 0})

    def handle_character(self, params: TypeHint.Params):
        if 'name' not in params:
            # e.g. fadetime=0 取消聚焦
            self.curr_char = None
            return
        if params.get('focus') in [-1, 0]:
            # 无效focus 取消聚焦
            self.curr_char = None
            return

        if 'focus' in params and params['focus'] != 1:
            key = 'name' + str(params['focus'])
            if key not in params:
                # 参见 gamedata/zh_CN/gamedata/story/obt/main\level_main_11-02_beg.txt
                # focus=3 [自由の角]
                return
            char = params[key]
        else:
            if 'name2' in params:
                # 双focus e.g. 蓝毒&格劳克斯
                self.curr_char = None
                return
            char = params['name']

        if '#' in char:
            char = char[:char.index('#')]
        if '$' in char:
            char = char[:char.index('$')]

        if char == 'char_empty':
            # 空角色
            self.curr_char = None
            return

        self.curr_char = Manager.npc(char)

    def handle_image(self, params: TypeHint.Params):
        if 'image' in params:
            self.during_img = True
        if len(params.keys()) == 1 and params.get('fadetime') == 0:
            self.during_img = False


class StoryParserManager:
    def __init__(self, lang: str, base: str, task_num: int = 10):
        self.base: str = base
        self.lang: str = lang
        self.task_num: int = task_num
        self.target: List[str] = []
        self.scan(base)

    def scan(self, base: str):
        files = os.listdir(base)
        for file in files:
            if file == '[uc]info':
                continue
            path = os.path.join(base, file)
            if os.path.isdir(path):
                self.scan(path)
            elif path.endswith('.txt'):
                self.target.append(path)

    async def runner(self):
        while self.target:
            target = self.target.pop(0)
            await StoryParser(self.lang, target).parse()

    async def run(self):
        await asyncio.gather(*[self.runner() for i in range(self.task_num)])

    def start(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.run())
