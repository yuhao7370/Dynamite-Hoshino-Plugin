import base64
import io
import json
import os
import random
import traceback
from decimal import *
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from hoshino import Service, priv
from hoshino.typing import CQEvent, MessageSegment

from .r_calc import calc_r
from .best20image import draw_best20
from .bomb import BombApi

sv = Service('Dynamite', manage_priv=priv.ADMIN, enable_on_default=True, visible=True)

bomb = BombApi("http://43.142.173.63:10483/v1")


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


def get_account(qq_id: str):
    account_path = os.path.join(os.path.dirname(__file__), 'account.json')
    with open(account_path, "r", encoding='utf8') as f:
        account = json.load(f)
    try:
        return True, account[qq_id]["uuid"]
    except Exception:
        return False, ""


@sv.on_prefix(('/dyR', '/dyr'))
async def command_r_calc(bot, ev: CQEvent):
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
async def command_bind(bot, ev: CQEvent):
    qq_id = ev.user_id
    username = ev.message.extract_plain_text().strip()
    username = username.strip()
    if(username == ""):
        await bot.finish(ev, f"绑定失败，请输入您的账号昵称")
    
    try:
        account_path = os.path.join(os.path.dirname(__file__), 'account.json')
        with open(account_path, "r", encoding='utf8') as f:
            account = json.load(f)

        user_id = bomb.get_user_by_name(username)["id"]

        try:
            old_name = account[str(qq_id)]["name"]

            account[str(qq_id)]["uuid"] = user_id
            account[str(qq_id)]["name"] = username
            await bot.send(ev, f"Q{qq_id}已成功换绑{username}\n原账号:{old_name}", at_sender=True)

        except Exception:
            account[str(qq_id)] = {}
            account[str(qq_id)]["uuid"] = user_id
            account[str(qq_id)]["name"] = username
            await bot.send(ev, f"Q{qq_id}已成功绑定{username}", at_sender=True)

        with open(account_path, 'w', encoding='utf8') as f:
            json.dump(account, f, indent=4, ensure_ascii=False)

    except Exception as e:
        traceback.print_exc()
        await bot.send(ev, f"绑定失败，{e}")


@sv.on_prefix(('/dyb20', '/b20', '/exb20'))
async def command_dyb20pic(bot, ev: CQEvent):
    qq_id = ev.user_id
    args = ev.message.extract_plain_text().strip().split()
    if(str(qq_id) == "2307957938"):
        await bot.finish(ev, f'不能查询NyaBye130的Best20成绩', at_sender=True)

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

    try:
        img = await draw_best20(bomb, user_id)
        base64str = img2b64(img)
        msg = MessageSegment.image(base64str)
        await bot.send(ev, msg)
    except Exception as e:
        await bot.send(ev, f"查询时出现错误：{e}")
    # await bot.send(ev, f'[CQ:image,file={img}]', at_sender=True)
    # await bot.finish(ev, f'{msg}', at_sender=True)


@sv.on_prefix(('/NyaBye130', '/nyabye130', '/NyaBye', '/nyabye', '/喵拜'))
async def command_nyabye(bot, ev: CQEvent):
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
    if(flag == True):
        res_path = os.path.join(os.path.dirname(__file__), "res")
        record_path = os.path.join(res_path, "NyaBye130")
        file_list = search_files(record_path, "wav")
        record_path = random.choice(file_list)
        voice_rec = MessageSegment.record(f'file:///{os.path.abspath(record_path)}')
        await bot.send(ev, voice_rec)

@sv.on_prefix(('/aplo', '/Aplo', '/Aploplex', '/aploplex'))
async def command_nyabye(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().strip().split()

    res_path = os.path.join(os.path.dirname(__file__), "res")
    record_path = os.path.join(res_path, "Aploplex")
    file_list = search_files(record_path, "wav")
    record_path = random.choice(file_list)
    voice_rec = MessageSegment.record(f'file:///{os.path.abspath(record_path)}')
    await bot.send(ev, voice_rec)