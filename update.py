from core.parser import Parser
from core.data import Manager

Parser('zh_CN')
Parser('en_US')
Parser('ja_JP')

Manager.save()
