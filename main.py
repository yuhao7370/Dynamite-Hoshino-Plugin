import os, traceback, random, base64, math, sqlite3, asyncio ,json, requests, io
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from decimal import *
from hoshino.config import SUPERUSERS
from hoshino import Service, priv ,util
from hoshino.typing import CQEvent, MessageSegment
from hoshino.log import new_logger
from io import BytesIO
# from aiocqhttp.message import MessageSegment

sv = Service('Dynamite', manage_priv = priv.ADMIN, enable_on_default = True, visible = True)

def SearchFiles(directory, fileType):      
    fileList=[]    
    for root, subDirs, files in os.walk(directory):
        for fileName in files:
            if fileName.endswith(fileType):
                fileList.append(os.path.join(root,fileName))
    return fileList

class DrawText:
    def __init__(self, 
                image: Image.Image,
                X: float,
                Y: float,
                size: int,
                text: str,
                font: str,
                color: tuple = (255, 255, 255, 255),
                stroke_width: int = 0,
                stroke_fill: tuple = (0, 0, 0, 0),
                anchor: str = 'lt') -> None:
        self._img = image
        self._pos = (X, Y)
        self._text = str(text)
        self._font = ImageFont.truetype(font, size)
        self._color = color
        self._stroke_width = stroke_width
        self._stroke_fill = stroke_fill
        self._anchor = anchor

    def draw_text(self) -> Image.Image:
        text_img = Image.new('RGBA', self._img.size, (255, 255, 255, 0))
        draw_img = ImageDraw.Draw(text_img)
        draw_img.text(self._pos, self._text, self._color, self._font, self._anchor, stroke_width=self._stroke_width, stroke_fill=self._stroke_fill)
        return Image.alpha_composite(self._img, text_img)

def genparallelogram(width, height, color):
    tan75 = 0.266
    img = Image.new(mode="RGB", size=(width, height), color = color)
    mask=Image.new('L', img.size, color=255)
    draw=ImageDraw.Draw(mask) 
    draw.polygon((0, 0, int(height * tan75), 0, 0, height), fill=0)
    draw.polygon((width, 0, width - int(height * tan75), height, width, height), fill=0)
    img.putalpha(mask)
    return img

def img_alpha(im, opacity):
    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im

def img2b64(img: Image.Image) -> str:
    bytesio = BytesIO()
    img.save(bytesio, 'PNG')
    bytes = bytesio.getvalue()
    base64_str = base64.b64encode(bytes).decode()
    return 'base64://' + base64_str

def open_img(img: str) -> Image.Image:
    with open(img, 'rb') as f:
        im = Image.open(f).convert('RGBA')
    return im

def song_illu_prehandle(path: str, wto, hto):
    img = open_img(path)
    w ,h = img.size
    tan75 = 0.266
    w ,h = img.size
    w2 = h * wto / hto
    h2 = w * hto / wto
    if(w / h *1.0 > wto / hto):
        img = img.crop(box = (int((w - w2) / 2), 0, int((w + w2) / 2), h))
    else:
        img = img.crop(box = (0, (int(h - h2) / 2), w, int((h + h2) / 2)))
    img = img.resize((wto, hto), Image.ANTIALIAS)
    width, height = img.size
    mask=Image.new('L', img.size, color=255)
    draw=ImageDraw.Draw(mask) 
    draw.polygon((0, 0, int(height * tan75), 0, 0, height), fill=0)
    draw.polygon((width, 0, width - int(height * tan75), height, width, height), fill=0)
    img.putalpha(mask)
    return img

def arrc(num:int):
    c = {}
    c[1] = 279.879794687164
    c[2] = 528.301077749884
    c[3] = 422.128204580857
    c[4] = 138.580738104051
    c[5] = 318.252118021848
    c[6] = -21.3604901556347
    c[7] = 89.799165984382
    c[8] = 256.769254208808
    c[9] = 110.044290813559
    c[10] = 25.6857362881284
    c[11] = -3.45575127827165
    c[12] = -11.2439540909426
    c[13] = -46.0356135329964
    c[14] = -42.4055325292137
    c[15] = -12.2459945433335
    c[16] = 8.91771876412662
    c[17] = 33.5454538433112
    c[18] = 33.216005109172
    c[19] = 29.9737147306553
    c[20] = 21.7501092277346
    c[21] = 4.69435084736257
    c[22] = -2.07316842598594
    c[23] = -8.52746692063741
    c[24] = -11.4173961727952
    c[25] = -13.7580079836705
    c[26] = -14.3051642335754
    c[27] = -8.34658365581463
    c[28] = -0.89353524074857
    c[29] = 0.714990388514441
    c[30] = 3.57845524206804
    c[31] = 3.79243682942648
    c[32] = 4.08195534054915
    c[33] = 6.23083840922214
    c[34] = 5.49378824597485
    c[35] = 1.69935797162909
    c[36] = -7.95468233626518E-02
    c[37] = -9.28951907355424E-02
    c[38] = -0.88520913997908
    c[39] = -0.965617394829134
    c[40] = -0.619991505598762
    c[41] = -1.48063492507091
    c[42] = -2.21198484168029
    c[43] = -1.15918404495256
    c[44] = 6.90824302578919E-02
    c[45] = 7.86488698968826E-02
    c[46] = 5.59550676107935E-03
    c[47] = 0.120475552036249
    c[48] = 0.194041976300861
    c[49] = 2.52469792567985E-02
    c[50] = 0.128790661891046
    c[51] = 0.42177821494088
    c[52] = 0.385782806557072
    c[53] = 7.51328698680896E-02
    c[54] = -8.02629465389211E-02
    c[55] = -1.31400067817723E-02

    return c[num]

def case(order: int):
    switcher = {
        5: 3,
        9: 4,
        14: 5,
        20: 6,
        27: 7,
        35: 8,
        44: 9,
        54: 10,
        65: 11
    }
    return switcher.get(order, -1)

def EVALCPOLY(order: int, logx: int, logy: int, x: float, y: float):
    tx ,ty, v= {}, {}, {}
    if(logx != 1):
        x = (x - (11.35)) / (5.65)
    else:
        x = (math.log(x) - (2.28683975944836)) / (0.546373584607856)

    if(logy != 1):
        y = (y - (0.9677015525)) / (0.0322984475)
    else:
        y = (math.log(y) - (-3.33888571301625E-02)) / (3.33888571301625E-02)

    tcnt = case(order)
    if(tcnt == -1):
        return 0.0

    if(tcnt > 6):
        if(x < -1): x = -1.0
        if(x > 1): x = 1.0
        if(y < -1): y = -1.0
        if(y > 1): y = 1.0
    tx[1] = 1.0
    ty[1] = 1.0
    tx[2] = x
    ty[2] = y
    for i in range(3, tcnt + 1, 1):
        tx[i] = 2 * x * tx[i - 1] - tx[i - 2]
        ty[i] = 2 * y * ty[i - 1] - ty[i - 2]
    iv = 1
    for i in range(1, tcnt + 1, 1):
        for j in range(i, 0, -1):
            v[iv] = tx[j] * ty[i - j + 1]
            iv = iv + 1
    z = 0.0
    for j in range(1 , order + 2, 1):
        z = z + arrc(j) * v[j]
    return z
    
def Chebyshev(rating: float, accuracy: float):
    return EVALCPOLY(54, 1, 1, rating, accuracy)

def image_draw(msg):
    fontpath = os.path.join(os.path.dirname(__file__), 'sy.ttf')
    font1 = ImageFont.truetype(fontpath, 16)
    width, height = font1.getsize_multiline(msg.strip())
    img = Image.new("RGB", (width + 20, height + 20), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), msg, fill=(0, 0, 0), font=font1)
    b_io = io.BytesIO()
    img.save(b_io, format="JPEG")
    base64_str = 'base64://' + base64.b64encode(b_io.getvalue()).decode()
    return base64_str

def ranks(score):
    res_path = os.path.join(os.path.dirname(__file__), "res")
    illustration_path = os.path.join(res_path, f"ranks/UI1_Difficulties_9.png")
    if(score == 1000000):                
        img = open_img(os.path.join(res_path, f"ranks/UI1_Difficulties_0.png"))
        return img
    elif( 980000 <= score < 1000000):
        img = open_img(os.path.join(res_path, f"ranks/UI1_Difficulties_1.png"))
        return img
    elif( 950000 <= score < 980000):
        img = open_img(os.path.join(res_path, f"ranks/UI1_Difficulties_2.png"))
        return img
    elif( 900000 <= score < 950000):
        img = open_img(os.path.join(res_path, f"ranks/UI1_Difficulties_3.png"))
        return img
    elif( 800000 <= score < 900000):
        img = open_img(os.path.join(res_path, f"ranks/UI1_Difficulties_4.png"))
        return img
    elif( 700000 <= score < 800000):
        img = open_img(os.path.join(res_path, f"ranks/UI1_Difficulties_5.png"))
        return img
    elif( 600000 <= score < 700000):
        img = open_img(os.path.join(res_path, f"ranks/UI1_Difficulties_6.png"))
        return img
    elif( 500000 <= score < 600000):
        img = open_img(os.path.join(res_path, f"ranks/UI1_Difficulties_7.png"))
        return img
    elif( 400000 <= score < 500000):
        img = open_img(os.path.join(res_path, f"ranks/UI1_Difficulties_8.png"))
        return img
    img = open_img(os.path.join(res_path, f"ranks/UI1_Difficulties_9.png"))
    return img

def get_account(qqid: str):
    account_path = os.path.join(os.path.dirname(__file__), 'account.json')
    with open(account_path, "r") as f:
        account = json.load(f)
    try:
        return True, account[qqid]["name"]
    except:
        return False, ""

@sv.on_prefix(('/dyR'))
async def Rcalc(bot, ev: CQEvent):
    qqid = ev.user_id

    args = ev.message.extract_plain_text().strip().split()

    if(len(args) == 2):
        try:
            Rating = float(args[0])
            acc = float(args[1]) / 100
        except:
            await bot.finish(ev, f'请输入合法的参数', at_sender=True)
        if(acc < 0.93 or Rating<5.6):
            R = int(acc * 100 / 2)
        else:
            chebyshev = Decimal(Chebyshev(Rating, acc)).quantize(Decimal("1"), rounding = "ROUND_HALF_UP")
            R = max(chebyshev, int(acc * 100 / 2))
        await bot.finish(ev, f'计算后R值:{R}\n误差为±1R', at_sender=True)
    elif(len(args) == 4):
        try:
            Rating = float(args[0])
            Perfect = int(args[1])
            Good = int(args[2])
            Miss = int(args[3])
        except:
            await bot.finish(ev, f'请输入合法的参数', at_sender=True)
        acc = (Perfect + Good / 2) / (Perfect + Good + Miss)
        if(acc < 0.93 or Rating<5.6):
            R = int(acc * 100 / 2)
        else:
            chebyshev = Decimal(Chebyshev(Rating, acc)).quantize(Decimal("1"), rounding = "ROUND_HALF_UP")
            R = max(chebyshev, int(acc * 100 / 2))
        await bot.finish(ev, f'计算后R值:{R}\n误差为±1R', at_sender=True)
    else:
        await bot.finish(ev, f'目前有两种计算方式\n/dyR 定数 Acc\n/dyR 定数 Perfect Good Miss', at_sender=True)

@sv.on_prefix(('/dy绑定', '/dybind'))
async def bind(bot, ev: CQEvent):
    qqid = ev.user_id
    userId = ev.message.extract_plain_text().strip()
    # await bot.send(ev, "1111111111111111111111111")
    try:   
        account_path = os.path.join(os.path.dirname(__file__), 'account.json')
        with open(account_path, "r") as f:
            account = json.load(f)
        
        idp = requests.post(f"http://43.142.173.63:10443/bomb/user/search/{userId}")
        id = json.loads(idp.content.decode("utf-8"))
        uuid = id["data"]["_id"]

        try:
            olduuid = account[str(qqid)]["uuid"]
            oldname = account[str(qqid)]["name"]

            account[str(qqid)]["uuid"] = uuid
            account[str(qqid)]["name"] = userId
            await bot.send(ev, f"Q{qqid}已成功换绑{userId}\n原账号:{oldname}",at_sender = True)

        except:
            account[str(qqid)] = {}
            account[str(qqid)]["uuid"] = uuid
            account[str(qqid)]["name"] = userId
            await bot.send(ev, f"Q{qqid}已成功绑定{userId}",at_sender = True)

        with open(account_path, 'w', encoding = 'utf8') as f:
            json.dump(account, f, indent = 4, ensure_ascii=False)

    except:
        await bot.send(ev, f"绑定失败，未找到账号{userId}")

@sv.on_prefix(('/textdyb20'))
async def dyb20(bot, ev: CQEvent):
    Difficulties = ["", "CASUAL",  "NORMAL", "HARD", "MEGA", "GIGA", "TERA"]
    qqid = ev.user_id
    args = ev.message.extract_plain_text().strip().split()
    if(len(args) == 1):
        userId = args[0]
        idp = requests.post(f"http://43.142.173.63:10443/bomb/user/search/{userId}")
        id = json.loads(idp.content.decode("utf-8"))
        userId = id["data"]["_id"] 
    else:
        userId = args[0]

    req = requests.get(f"http://43.142.173.63:10443/bomb/user/{userId}/best20r")
    info = json.loads(req.content.decode("utf-8"))
    info = info ["data"]
    msg = ""
    illegal = ""
    totalr = 0
    for song in info:
        chartId = song ["chartId"]
        chartp = requests.get(f"http://43.142.173.63:10443/bomb/chart/{chartId}")
        chartinfo = chartp.content.decode("utf-8")
        # await bot.send(ev, chartinfo)
        #await bot.send(ev, f'{chartinfo}')
        chartinfo = json.loads(chartinfo)
        try:
            diff = Difficulties[chartinfo["data"]["difficultyClass"]] + str(chartinfo["data"]["difficultyValue"])
        except:
            illegal += f'发现非法谱面{chartId}\n'

        sets = requests.post(f"http://43.142.173.63:10443/bomb/set/by-chart/{chartId}")
        songinfo = sets.content.decode("utf-8")
        songinfo = json.loads(songinfo)
        try:
            songinfo = songinfo["data"]
            R = Decimal(song["RScore"]).quantize(Decimal("1"), rounding = "ROUND_HALF_UP")
            totalr += R
            msg += songinfo["musicName"] + f"\n{diff} " +"R:" + str(R) + "\n\n"
        except:
            msg += songinfo["musicName"] + f"\n{diff} " +"R:" + str(R) + "\n\n"
            R = 0
        
        # await bot.send(ev, f'{songinfo}')
    msg += "TotalR: " + str(totalr)
    if(illegal!=""):
        await bot.send(ev, illegal)
    pic = image_draw(msg)
    msg = MessageSegment.image(pic)
    await bot.finish(ev, msg)   
    #await bot.send(ev, f'[CQ:image,file={pic}]', at_sender=True)
    # await bot.finish(ev, f'{msg}', at_sender=True)


@sv.on_prefix(('/dyb20'))
async def dyb20pic(bot, ev: CQEvent):
    Difficulties = ["", "CASUAL",  "NORMAL", "HARD", "MEGA", "GIGA", "TERA"]
    qqid = ev.user_id
    args = ev.message.extract_plain_text().strip().split()
    # if(qqid == "2307957938"):  
    #     await bot.finish(ev, f'不能查询NyaBye130的Best20成绩', at_sender=True)
    if(len(args) == 1):
        userId = args[0]
        idp = requests.post(f"http://43.142.173.63:10443/bomb/user/search/{userId}")
        id = json.loads(idp.content.decode("utf-8"))
        userId = id["data"]["_id"] 
        username = id["data"]["username"]
    else:
        flag, userId = get_account(str(qqid))
        if(flag == False):
            await bot.finish(ev, f'您还未绑定，请用/dybind指令绑定', at_sender=True)
        else:
            idp = requests.post(f"http://43.142.173.63:10443/bomb/user/search/{userId}")
            id = json.loads(idp.content.decode("utf-8"))
            userId = id["data"]["_id"] 
            username = id["data"]["username"]

    await bot.send(ev, f'正在查询{username}的Best20成绩', at_sender=True)
    recordlist = []

    req = requests.get(f"http://43.142.173.63:10443/bomb/user/{userId}/best20r")
    info = json.loads(req.content.decode("utf-8"))
    info = info ["data"]
    illegal = ""
    totalr = 0
    res_path = os.path.join(os.path.dirname(__file__), "res")
    for song in info:
        chartId = song ["chartId"]
        chartp = requests.get(f"http://43.142.173.63:10443/bomb/chart/{chartId}")
        chartinfo = chartp.content.decode("utf-8")
        #await bot.send(ev, f'{chartinfo}')
        # await bot.send(ev, chartinfo)
        chartinfo = json.loads(chartinfo)
        try:
            diff = Difficulties[chartinfo["data"]["difficultyClass"]] + str(chartinfo["data"]["difficultyValue"])
        except:
            illegal += f'发现非法谱面{chartId}\n'
            continue

        sets = requests.post(f"http://43.142.173.63:10443/bomb/set/by-chart/{chartId}")
        songinfo = sets.content.decode("utf-8")
        # await bot.send(ev, songinfo)
        songinfo = json.loads(songinfo)
        try:
            songinfo = songinfo["data"]
            _id = songinfo['_id']
            R = Decimal(song["RScore"]).quantize(Decimal("1"), rounding = "ROUND_HALF_UP")
            totalr += R
        except:
            try:
                # songinfo = songinfo["data"]
                _id = songinfo['_id']
                R = 0
            except:
                print(songinfo)
                continue
        
        recordlist.append((songinfo["musicName"], _id, chartinfo["data"]["difficultyClass"], chartinfo["data"]["difficultyValue"], song ["score"], song["scoreDetail"], R))

    BackGround_path = os.path.join(res_path, "BackGround.png")
    img = open_img(BackGround_path)
    # img = open_img("res/test.png")
    #illusize = 408 230 ------x1097 y317
    x0, y0 = 196, 682
    whitep = genparallelogram(83, 44, "#ffffff")
    levelp = {}
    levelp["TERA"] = genparallelogram(164, 92, "#000000")
    levelp["GIGA"] = genparallelogram(164, 92, "#6F6F6F")
    levelp["MEGA"] = genparallelogram(164, 92, "#F601FF")
    levelp["HARD"] = genparallelogram(164, 92, "#BE2D23")
    levelp["NORMAL"] = genparallelogram(164, 92, "#3173B3")
    levelp["CASUAL"] = genparallelogram(164, 92, "#51AF44") 
    phifont = os.path.join(os.path.dirname(__file__), 'sy.ttf')
    now = 1
    for song in recordlist:
        if(now % 2 == 0):
            x = x0 + 1097
            y = y0 + (int(now / 2) - 1) * 317
            y += 105
        else:
            x = x0
            y = y0 + (int(now / 2)) * 317

        song_name = song[0]
        song_id = song[1]
        song_diff = Difficulties[song[2]]
        song_rating = song[3]
        song_score = song[4]
        song_pgm = song[5]
        scoreDetail = song_pgm
        # print(scoreDetail)
        song_R = song[6]
            
        illustration_path = os.path.join(res_path, f"{song_id}.webp")
        try:
            illu = song_illu_prehandle(illustration_path, 408, 230) #背景和曲绘
        except:
            continue

        img.alpha_composite(whitep, (x - 21, y)) #白色平行四边形
        img = DrawText(img, x + 20, y + 22, 30, f"#{now}", phifont, (0, 0, 0, 255), anchor='mm').draw_text()
        img.alpha_composite(illu , (x, y)) #曲绘  
        img.alpha_composite(levelp[song_diff], (x - 72, y + 138)) #难度对应平行四边形  
        # acc = Decimal(song[4]).quantize(Decimal("0.01"), rounding = "ROUND_HALF_UP")
        img = DrawText(img, x + 16 , y + 163, 26, f"{song_diff} {str(song_rating)}", phifont, (255, 255, 255, 255), anchor='mm').draw_text() #难度 定数
        img = DrawText(img, x + 9, y + 198, 38, f"R:{song_R}", phifont, (255, 255, 255, 255), anchor='mm').draw_text() #单曲R
        img = DrawText(img, x + 655, y + 44, 32, f"{song_name}", phifont, (255, 255, 255, 255), anchor='mm').draw_text() #曲名
        
        img = DrawText(img, x + 530, y + 131, 37, f"{song_score}".zfill(7), phifont, (255, 255, 255, 255), anchor='ls').draw_text() #分数
        p, g, m = scoreDetail["perfect"], scoreDetail["good"], scoreDetail["miss"]
        acc = Decimal((p + g * 0.5) / (p + g + m) * 100.0).quantize(Decimal("0.01"), rounding = "ROUND_HALF_UP")
        img = DrawText(img, x + 738, y + 131, 27, f"{acc}%", phifont, (255, 255, 255, 255), anchor='ls').draw_text() #acc
        
        rankimg = ranks(song_score)
        rankimg = rankimg.resize((115, 115), Image.ANTIALIAS)
        img.alpha_composite(rankimg , (x + 392, y + 80)) #等级       
            
        
        p, g, m = int(p), int(g), int(m)
        img = DrawText(img, x + 525, y + 190, 22, f"Perfect", phifont, (255, 183, 0, 255), anchor='ls').draw_text() #P
        img = DrawText(img, x + 630, y + 181, 22, f"{p}", phifont, (255, 255, 255, 255), anchor='mm').draw_text() #P
        img = DrawText(img, x + 663, y + 190, 22, f"Good", phifont, (76, 171, 255, 255), anchor='ls').draw_text() #G
        img = DrawText(img, x + 740, y + 181, 22, f"{g}", phifont, (255, 255, 255, 255), anchor='mm').draw_text() #G
        img = DrawText(img, x + 765, y + 190, 22, f"Miss", phifont, (255, 76, 76, 255), anchor='ls').draw_text() #M
        img = DrawText(img, x + 837, y + 181, 22, f"{m}", phifont, (255, 255, 255, 255), anchor='mm').draw_text() #M

  
        now += 1     

    img = DrawText(img, 1430, 330, 68, f"Player: {username}", phifont, (255, 255, 255, 255), anchor='ls').draw_text() #玩家名称
    img = DrawText(img, 1430, 430, 68, f"TotalR20Score: {totalr}", phifont, (255, 255, 255, 255), anchor='ls').draw_text() #rks
    
    # img = DrawText(img, 1110, 4513, 72, f"Rks Generator Betav0.1", phifont, (255, 255, 255, 255), anchor='mm').draw_text()
    base64str = img2b64(img)
    msg = MessageSegment.image(base64str)
    await bot.send(ev, msg)    
    print(illegal)
    # await bot.send(ev, f'[CQ:image,file={img}]', at_sender=True)
    # await bot.finish(ev, f'{msg}', at_sender=True)

@sv.on_prefix(('/NyaBye130','/nyabye130','/NyaBye','/nyabye','/喵拜'))
async def nyabye(bot, ev: CQEvent):
    qqid = ev.user_id
    args = ev.message.extract_plain_text().strip().split()
    if(args[0] == "overdose"):
        res_path = os.path.join(os.path.dirname(__file__), "res")
        record_path = os.path.join(res_path, "NYABYE130 OVERDOSE.wav")
        voice_rec = MessageSegment.record(f'file:///{os.path.abspath(record_path)}')
        await bot.finish(ev, voice_rec)

    res_path = os.path.join(os.path.dirname(__file__), "res")
    record_path = os.path.join(res_path, "NyaBye130")
    list = SearchFiles(record_path, "wav")
    record_path = random.choice(list)
    voice_rec = MessageSegment.record(f'file:///{os.path.abspath(record_path)}')
    await bot.send(ev, voice_rec)
