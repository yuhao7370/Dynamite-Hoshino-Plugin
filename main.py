# noinspection SpellCheckingInspection
"""
根据 Apache 协议在此列出文件修改：

将以下方法移除：
- img_alpha

将以下函数移动到 `best20image.py` 中：
- open_img 改名为 open_image
- genparallogram 改名为 get_parallelogram_image
- song_illu_prehandle 改名为 get_illustration_image
- 将 DrawText 类合并简化为 draw_text
- ranks 改名为 get_score_rank_image

将以下函数移动到 `r_calc.py` 中：
- case
- arrc
- EVALCPOLY 改名为 eval_chebyshev_poly
- Chebyshev 改名为 calc_r

修改本文文件中的以下方法：
- 除 dyb20pic 外均改变函数与/或变量名称
- dyb20pic 将图片生成部分抽取到 `best20image.py` 中的 draw_best20 函数中

"""

import base64
import io
import json
import os
import random
import traceback
from decimal import *
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont

from bomb import BombApi
from best20image import draw_best20
from r_calc import calc_r
from hoshino import Service, priv
from hoshino.typing import CQEvent, MessageSegment

sv = Service('Dynamite', manage_priv=priv.ADMIN, enable_on_default=True, visible=True)

bomb = BombApi("http://localhost:10443/v1")


def search_files(directory, file_extension):
    file_list = []
    for root, sub_dirs, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith(file_extension):
                file_list.append(os.path.join(root, file_name))
    return file_list


def img2b64(img: Image.Image) -> str:
    bytesio = BytesIO()
    img.save(bytesio, 'PNG')
    image_bytes = bytesio.getvalue()
    base64_str = base64.b64encode(image_bytes).decode()
    return 'base64://' + base64_str


def image_draw(msg):
    font_path = os.path.join(os.path.dirname(__file__), 'sy.ttf')
    font1 = ImageFont.truetype(font_path, 16)
    width, height = font1.getsize_multiline(msg.strip())
    img = Image.new("RGB", (width + 20, height + 20), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), msg, fill=(0, 0, 0), font=font1)
    b_io = io.BytesIO()
    img.save(b_io, format="JPEG")
    base64_str = 'base64://' + base64.b64encode(b_io.getvalue()).decode()
    return base64_str


def get_account(qq_id: str):
    account_path = os.path.join(os.path.dirname(__file__), 'account.json')
    with open(account_path, "r", encoding='utf8') as f:
        account = json.load(f)
    try:
        return True, account[qq_id]["name"]
    except Exception:
        return False, ""


@sv.on_prefix('/dyR')
async def r_calc(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().strip().split()

    if len(args) == 2:
        try:
            rating = float(args[0])
            acc = float(args[1]) / 100
        except Exception:
            await bot.finish(ev, f'请输入合法的参数', at_sender=True)
            return
        if acc < 0.93 or rating < 5.6:
            r = int(acc * 100 / 2)
        else:
            chebyshev = Decimal(calc_r(rating, acc)).quantize(Decimal("1"), rounding="ROUND_HALF_UP")
            r = max(chebyshev, Decimal(acc * 100 / 2))
        await bot.finish(ev, f'计算后R值:{r}\n误差为±1R', at_sender=True)
    elif len(args) == 4:
        try:
            rating = float(args[0])
            perfect = int(args[1])
            good = int(args[2])
            miss = int(args[3])
        except Exception:
            await bot.finish(ev, f'请输入合法的参数', at_sender=True)
            return
        acc = (perfect + good / 2) / (perfect + good + miss)
        if acc < 0.93 or rating < 5.6:
            r = int(acc * 100 / 2)
        else:
            chebyshev = Decimal(calc_r(rating, acc)).quantize(Decimal("1"), rounding="ROUND_HALF_UP")
            r = max(chebyshev, Decimal(acc * 100 / 2))
        await bot.finish(ev, f'计算后R值:{r}\n误差为±1R', at_sender=True)
    else:
        await bot.finish(ev, f'目前有两种计算方式\n/dyR 定数 Acc\n/dyR 定数 perfect good miss', at_sender=True)


@sv.on_prefix(('/dy绑定', '/dybind'))
async def bind(bot, ev: CQEvent):
    qq_id = ev.user_id
    userId = ev.message.extract_plain_text().strip()
    userId = userId.strip()
    # await bot.send(ev, "1111111111111111111111111")
    try:
        account_path = os.path.join(os.path.dirname(__file__), 'account.json')
        with open(account_path, "r", encoding='utf8') as f:
            account = json.load(f)

        idp = requests.post(f"http://43.142.173.63:10443/bomb/user/search/{userId}")
        user_info = json.loads(idp.content.decode("utf-8"))
        uuid = user_info["data"]["_id"]

        try:
            old_name = account[str(qq_id)]["name"]

            account[str(qq_id)]["uuid"] = uuid
            account[str(qq_id)]["name"] = userId
            await bot.send(ev, f"Q{qq_id}已成功换绑{userId}\n原账号:{old_name}", at_sender=True)

        except Exception:
            account[str(qq_id)] = {}
            account[str(qq_id)]["uuid"] = uuid
            account[str(qq_id)]["name"] = userId
            await bot.send(ev, f"Q{qq_id}已成功绑定{userId}", at_sender=True)

        with open(account_path, 'w', encoding='utf8') as f:
            json.dump(account, f, indent=4, ensure_ascii=False)

    except Exception as e:
        traceback.print_exc()
        await bot.send(ev, f"绑定失败，{e}")


# @sv.on_prefix('/textdyb20')
# async def dyb20(bot, ev: CQEvent):
#     Difficulties = ["", "CASUAL", "NORMAL", "HARD", "MEGA", "GIGA", "TERA"]
#     qq_id = ev.user_id
#     args = ev.message.extract_plain_text().strip().split()
#     if len(args) == 1:
#         userId = args[0]
#         idp = requests.post(f"http://43.142.173.63:10443/bomb/user/search/{userId}")
#         id = json.loads(idp.content.decode("utf-8"))
#         userId = id["data"]["_id"]
#     else:
#         userId = args[0]
#
#     req = requests.get(f"http://43.142.173.63:10443/bomb/user/{userId}/best20r")
#     info = json.loads(req.content.decode("utf-8"))
#     info = info["data"]
#     msg = ""
#     illegal = ""
#     total_r = 0
#     for song in info:
#         chartId = song["chartId"]
#         chart_p = requests.get(f"http://43.142.173.63:10443/bomb/chart/{chartId}")
#         chart_info = chart_p.content.decode("utf-8")
#         # await bot.send(ev, chart_info)
#         # await bot.send(ev, f'{chart_info}')
#         chart_info = json.loads(chart_info)
#         try:
#             diff = Difficulties[chart_info["data"]["difficultyClass"]] + str(chart_info["data"]["difficultyValue"])
#         except Exception:
#             illegal += f'发现非法谱面{chartId}\n'
#
#         sets = requests.post(f"http://43.142.173.63:10443/bomb/set/by-chart/{chartId}")
#         song_info = sets.content.decode("utf-8")
#         song_info = json.loads(song_info)
#         try:
#             song_info = song_info["data"]
#             R = Decimal(song["RScore"]).quantize(Decimal("1"), rounding="ROUND_HALF_UP")
#             total_r += R
#             msg += song_info["musicName"] + f"\n{diff} " + "R:" + str(R) + "\n\n"
#         except Exception:
#             msg += song_info["musicName"] + f"\n{diff} " + "R:" + str(R) + "\n\n"
#             R = 0
#
#         # await bot.send(ev, f'{song_info}')
#     msg += "TotalR: " + str(total_r)
#     if illegal != "":
#         await bot.send(ev, illegal)
#     pic = image_draw(msg)
#     msg = MessageSegment.image(pic)
#     await bot.finish(ev, msg)
#     # await bot.send(ev, f'[CQ:image,file={pic}]', at_sender=True)
#     # await bot.finish(ev, f'{msg}', at_sender=True)


# @sv.on_prefix(('/dytest'))
# async def dytest(bot, ev: CQEvent):
#     Difficulties = ["", "CASUAL",  "NORMAL", "HARD", "MEGA", "GIGA", "TERA"]
#     qqid = ev.user_id
#     args = ev.message.extract_plain_text().strip().split()
#     # if(qqid == "2307957938"):
#     #     await bot.finish(ev, f'不能查询NyaBye130的Best20成绩', at_sender=True)
#     if(len(args) == 1):
#         userId = args[0]
#         await bot.send(ev, userId)
#         idp = requests.post(f"http://43.142.173.63:10443/bomb/user/search/{userId}")

#         id = json.loads(idp.content.decode("utf-8"))
#         userId = id["data"]["_id"]
#         username = id["data"]["username"]

@sv.on_prefix('/dyb20')
async def dyb20pic(bot, ev: CQEvent):
    qq_id = ev.user_id
    args = ev.message.extract_plain_text().strip().split()
    # if(qq_id == "2307957938"):
    #     await bot.finish(ev, f'不能查询NyaBye130的Best20成绩', at_sender=True)

    if len(args) == 1:
        username = args[0]
        user_id = bomb.get_user_by_name(username)["id"]
    else:
        flag, user_id = get_account(str(qq_id))
        if not flag:
            await bot.finish(ev, f'您还未绑定，请用/dybind指令绑定', at_sender=True)
            return
        else:
            username = bomb.get_user(user_id)["username"]

    await bot.send(ev, f'正在查询{username}的Best20成绩', at_sender=True)

    img = draw_best20(user_id)
    base64str = img2b64(img)
    msg = MessageSegment.image(base64str)
    await bot.send(ev, msg)
    # await bot.send(ev, f'[CQ:image,file={img}]', at_sender=True)
    # await bot.finish(ev, f'{msg}', at_sender=True)


@sv.on_prefix(('/NyaBye130', '/nyabye130', '/NyaBye', '/nyabye', '/喵拜'))
async def nyabye(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().strip().split()
    flag = True
    try:
        if args[0] == "overdose":
            res_path = os.path.join(os.path.dirname(__file__), "res")
            record_path = os.path.join(res_path, "NYABYE130 OVERDOSE.wav")
            voice_rec = MessageSegment.record(f'file:///{os.path.abspath(record_path)}')
            flag = False
            await bot.finish(ev, voice_rec)
    except Exception:
        flag = True
    if flag:
        res_path = os.path.join(os.path.dirname(__file__), "res")
        record_path = os.path.join(res_path, "NyaBye130")
        file_list = search_files(record_path, "wav")
        record_path = random.choice(file_list)
        voice_rec = MessageSegment.record(f'file:///{os.path.abspath(record_path)}')
        await bot.send(ev, voice_rec)
