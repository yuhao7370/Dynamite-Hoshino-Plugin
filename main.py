import base64
from enum import Flag
import io
import json
import os
import random
import traceback
from decimal import *
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from hoshino import Service, priv, util
from hoshino.typing import CQEvent, MessageSegment

from .avatar import *
from .r_calc import calc_r
from .rrank import get_tops
from .register import register
from .best20image import *
from .bomb import BombApi

sv = Service('Dynamite', manage_priv=priv.ADMIN, enable_on_default=True, visible=True)

bomb = BombApi("http://43.142.173.63:10483/bomb/v2")


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

@sv.on_prefix(('/dyreg'))
async def command_register_admin(bot, ev: CQEvent):
    admin_list = ["2737723325", "3070190799", "1580885360", "520127606", "1255710289", "2539990262"]
    qq_id = ev.user_id
    if(str(qq_id) not in admin_list):
        await bot.finish(ev, f'您不是Explode管理员，请找管理员注册账号', at_sender=True)
        return
    
    args = ev.message.extract_plain_text().strip().split()
    try:
        username = args[0]
        password = args[1]
    except:
        await bot.finish(ev, f'格式为/dyreg 昵称 密码', at_sender=True)
        return
    
    flag, msg = register(username, password)
    if(flag == True):
        await bot.finish(ev, f'玩家{username}注册成功，uid为{msg}', at_sender=True)
    else:
        await bot.finish(ev, f'注册时出现问题: {msg}', at_sender=True)

@sv.on_prefix(('/dya', '/dyavatar'))
async def command_avatar_upload(bot, ev: CQEvent):
    qq_id = ev.user_id
    flag, user_id = get_account(str(qq_id))
    if not flag:
        await bot.finish(ev, f'您还未绑定，请用/dybind指令绑定', at_sender=True)
        return
    flag = upload_avatar(qq_id, user_id)
    username = bomb.get_user(user_id)["username"]
    if(flag == True):
        await bot.finish(ev, f'玩家{username}已更新为Q{qq_id}的头像', at_sender=True)
    else:
        await bot.finish(ev, f'头像更新失败', at_sender=True)

# @sv.on_prefix(('/dyleaderboard', '/dyl'))
# async def command_dyleaderboard(bot, ev: CQEvent):
#     await bot.send(ev, "正在更新排行榜")
#     tops = get_tops()
#     msg = "Explode Leaderboard:\n"
#     for i in range(0, len(tops)):
#         msg += f"#{i + 1}\n"
#         msg += f"{tops[i]['username']}  R:{tops[i]['R']} \n"
#     await bot.finish(ev, msg)

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

@sv.on_prefix(('/dyrecent', '/dyre', '/exre', '/exrecent'))
async def command_dyrecentpic(bot, ev: CQEvent):
    qq_id = ev.user_id
    args = ev.message.extract_plain_text().strip().split()
    # if(str(qq_id) == "2307957938"):
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

    await bot.send(ev, f'正在查询{username}的Recent成绩', at_sender=True)
    try:
        recentDict = bomb.get_user_recent_records(user_id)
        record = recentDict[0]
        
        score = record["score"]
        perfect = record["perfect"]
        good = record["good"]
        miss = record["miss"]
        chartId = record["chartId"]
            
        try:
            chart_info = bomb.get_chart(chartId)
            # print(chart_info)
        except Exception:
            await bot.finish(ev, f"查询时出现错误：{Exception}")
            return
        difficultyClass = chart_info["difficultyClass"]
        difficultyValue = chart_info["difficultyValue"]
        difficultyText = get_difficulty_class_text(difficultyClass)
        # print(chart_info)
        try:
            setInfo = bomb.get_set(chart_info["parentSetId"])
        except Exception:
            await bot.finish(ev, f"查询时出现错误：{Exception}")
            return
        set_id = setInfo["id"]
        musicName = setInfo["musicName"]
        r = Decimal(record["r"] or 0).quantize(Decimal("1"), rounding="ROUND_HALF_UP")
        try:
            accuracy = Decimal((perfect + good * 0.5) / (perfect + good + miss) * 100.0).quantize(Decimal("0.01"),
                                                                                                rounding="ROUND_HALF_UP")
        except:
            accuracy = "0.00"     
        illustration_path = os.path.join(resource_path, f"{set_id}.webp")
        try:
            illustration_image = get_illustration_image(illustration_path, 408, 230)
        except Exception:
            try:
                url = f"http://43.142.173.63:5244/d/download/cover/480x270_jpg/{set_id}"
                downloadimg(url, illustration_path)
                illustration_image = get_illustration_image(illustration_path, 408, 230)
                # print(set_id)
            # f"http://43.142.173.63:5244/d/download/cover/480x270_jpg/{set_id}"
            except Exception:
                await bot.finish(ev, f"查询时出现错误：{Exception}")
                return
        img = MessageSegment.image(util.pic2b64(illustration_image))
        await bot.send(ev, f"{img}\n{musicName} {difficultyText}{difficultyValue}\n{score} {accuracy}% R:{r}\n{perfect}-{good}-{miss}")
    except Exception as e:
        await bot.send(ev, f"查询时出现错误：{e}")


@sv.on_prefix(('/dyb20', '/b20', '/exb20'))
async def command_dyb20pic(bot, ev: CQEvent):
    qq_id = ev.user_id
    args = ev.message.extract_plain_text().strip().split()
    # if(str(qq_id) == "2307957938"):
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
            # print(bomb.get_user(user_id))
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
async def command_aplo(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().strip().split()

    res_path = os.path.join(os.path.dirname(__file__), "res")
    record_path = os.path.join(res_path, "Aploplex")
    file_list = search_files(record_path, "wav")
    record_path = random.choice(file_list)
    voice_rec = MessageSegment.record(f'file:///{os.path.abspath(record_path)}')
    await bot.send(ev, voice_rec)