
import os
import json
from enum import Enum


class Json_Flag(Enum):
    SUCCESS = 0
    NO_FILE = 1
    ERR_OPEN_R = 2
    ERR_OPEN_W = 3
    EMPTY_DICT = 4


class Parse_Json():
    def __init__(self, _file):
        self.file = _file

    def file_read(self):
        self.json_dict = {}
        if not os.path.exists(self.file):
            return (Json_Flag.NO_FILE, self.json_dict)

        try:
            with open(self.file, mode='r', encoding="utf-8") as fp:
                self.json_dict = json.load(fp)
        except Exception:
            return (Json_Flag.ERR_OPEN_R, self.json_dict)

        if not self.json_dict:
            return (Json_Flag.EMPTY_DICT, self.json_dict)

        return (Json_Flag.SUCCESS, self.json_dict)

    def file_write(self, _json_dict={}):
        if not os.path.exists(self.file):
            return Json_Flag.NO_FILE

        try:
            with open(self.file, mode='w+', encoding="utf-8") as fp:
                json.dump(_json_dict, fp, indent=4, ensure_ascii=False)
        except Exception:
            return Json_Flag.ERR_OPEN_W

        return Json_Flag.SUCCESS

