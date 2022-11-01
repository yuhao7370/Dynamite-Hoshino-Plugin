import base64
from enum import Flag
import io
import json
import os
import random
import traceback
from decimal import *
from io import BytesIO
from .best20image import draw_best20

from PIL import Image, ImageDraw, ImageFont

from .bomb import BombApi
bomb = BombApi("http://43.142.173.63:10483/v1")

def get_account(qq_id: str):
    account_path = os.path.join(os.path.dirname(__file__), 'account.json')
    with open(account_path, "r", encoding='utf8') as f:
        account = json.load(f)
    try:
        return True, account[qq_id]["uuid"]
    except Exception:
        return False, ""

if __name__ == '__main__':
    qq_id = "2737723325"
    # if(str(qq_id) == "2307957938"):
    #     await bot.finish(ev, f'不能查询NyaBye130的Best20成绩', at_sender=True)
    flag, user_id = get_account(str(qq_id))
    img = draw_best20(bomb, user_id)
    img.show()
