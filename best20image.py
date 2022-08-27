import os
from decimal import Decimal

from PIL import Image, ImageDraw, ImageFont

from .bomb import BombApi

tan75 = 0.266

resource_path = os.path.join(os.path.dirname(__file__), "res")
phi_font_path = os.path.join(os.path.dirname(__file__), 'sy.ttf')

difficulty_texts = [
    "UNKNOWN",
    "CASUAL",
    "NORMAL",
    "HARD",
    "MEGA",
    "GIGA",
    "TERA"
]


def get_difficulty_class_text(difficulty_class):
    return difficulty_texts[difficulty_class]


def open_image(image_path: str) -> Image.Image:
    with open(image_path, "rb") as file:
        return Image.open(file).convert("RGBA")


def get_parallelogram_image(width, height, color) -> Image:
    image = Image.new(mode="RGB", size=(width, height), color=color)
    mask = Image.new('L', image.size, color=255)
    draw = ImageDraw.Draw(mask)
    draw.polygon((0, 0, int(height * tan75), 0, 0, height), fill=0)
    draw.polygon((width, 0, width - int(height * tan75), height, width, height), fill=0)
    image.putalpha(mask)
    return image


def get_illustration_image(path, wto, hto) -> Image:
    image = open_image(path)
    w, h = image.size
    w2 = h * wto / hto
    h2 = w * hto / wto
    if w / h * 1.0 > wto / hto:
        image = image.crop(box=(int((w - w2) / 2), 0, int((w + w2) / 2), h))
    else:
        image = image.crop(box=(0, int((h - h2) / 2), w, int((h + h2) / 2)))
    image = image.resize((wto, hto), Image.ANTIALIAS)
    width, height = image.size
    mask = Image.new('L', image.size, color=255)
    draw = ImageDraw.Draw(mask)
    draw.polygon((0, 0, int(height * tan75), 0, 0, height), fill=0)
    draw.polygon((width, 0, width - int(height * tan75), height, width, height), fill=0)
    image.putalpha(mask)
    return image


def draw_text(
        image: Image.Image,
        position,
        text: str,
        font_size: int,
        font_path: str,
        color: tuple = (255, 255, 255, 255),
        stroke_width: int = 0,
        stroke_fill: tuple = (0, 0, 0, 0),
        anchor: str = "lt"
) -> Image.Image:
    font = ImageFont.truetype(font_path, font_size)
    text_image = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw_image = ImageDraw.Draw(text_image)
    draw_image.text(position, text, color, font, anchor, stroke_width=stroke_width, stroke_fill=stroke_fill)
    return Image.alpha_composite(image, text_image)


difficulty_parallelograms = [
    get_parallelogram_image(83, 44, "#FFFFFF"),
    get_parallelogram_image(164, 92, "#51AF44"),
    get_parallelogram_image(164, 92, "#3173B3"),
    get_parallelogram_image(164, 92, "#BE2D23"),
    get_parallelogram_image(164, 92, "#F601FF"),
    get_parallelogram_image(164, 92, "#6F6F6F"),
    get_parallelogram_image(164, 92, "#000000"),
]

background_parallelograms = difficulty_parallelograms[0]


def get_score_rank_image(score) -> Image.Image:
    if score == 1000000:
        return open_image(os.path.join(resource_path, "ranks/UI1_Difficulties_0.png"))
    elif 980000 <= score < 1000000:
        return open_image(os.path.join(resource_path, "ranks/UI1_Difficulties_1.png"))
    elif 950000 <= score < 980000:
        return open_image(os.path.join(resource_path, "ranks/UI1_Difficulties_2.png"))
    elif 900000 <= score < 950000:
        return open_image(os.path.join(resource_path, "ranks/UI1_Difficulties_3.png"))
    elif 800000 <= score < 900000:
        return open_image(os.path.join(resource_path, "ranks/UI1_Difficulties_4.png"))
    elif 700000 <= score < 800000:
        return open_image(os.path.join(resource_path, "ranks/UI1_Difficulties_5.png"))
    elif 600000 <= score < 700000:
        return open_image(os.path.join(resource_path, "ranks/UI1_Difficulties_6.png"))
    elif 500000 <= score < 600000:
        return open_image(os.path.join(resource_path, "ranks/UI1_Difficulties_7.png"))
    elif 400000 <= score < 500000:
        return open_image(os.path.join(resource_path, "ranks/UI1_Difficulties_8.png"))
    else:
        return open_image(os.path.join(resource_path, "ranks/UI1_Difficulties_9.png"))


def draw_best20(bomb: BombApi, user_id: str):
    username = bomb.get_user(user_id)["username"]
    records = bomb.get_user_best_records_r_value(user_id)

    background_path = os.path.join(resource_path, "BackGround.png")
    image = open_image(background_path)
    x0, y0 = 196, 682

    total_r = 0
    count = 1
    for record in records:
        # 收集数据
        score = record["score"]
        perfect = record["perfect"]
        good = record["good"]
        miss = record["miss"]
        chart_id = record["chart-id"]
        try:
            chart_info = bomb.get_chart(chart_id)
        except Exception:
            continue
        difficulty_num = chart_info["difficulty-class"]
        difficulty_value = chart_info["difficulty-value"]
        difficulty_text = get_difficulty_class_text(difficulty_num)
        # print(chart_info)
        try:
            set_info = bomb.get_set(chart_info["included-in"])
        except Exception:
            continue
        set_id = set_info["id"]
        music_name = set_info["music-name"]
        r = Decimal(record["r"] or 0).quantize(Decimal("1"), rounding="ROUND_HALF_UP")
        total_r += r

        # 绘制
        if count % 2 == 0:
            x = x0 + 1097
            y = y0 + (int(count / 2) - 1) * 317
            y += 105
        else:
            x = x0
            y = y0 + (int(count / 2)) * 317

        # 背景大图
        illustration_path = os.path.join(resource_path, f"{set_id}.webp")
        try:
            illustration_image = get_illustration_image(illustration_path, 408, 230)
        except Exception:
            continue

        # 底部白色背景
        image.alpha_composite(background_parallelograms, (x - 21, y))
        # 左上角编号
        image = draw_text(image, (x + 20, y + 22), f"#{count}", 30, phi_font_path, (0, 0, 0, 255), anchor="mm")
        # 曲绘
        image.alpha_composite(illustration_image, (x, y))
        # 难度标志背景
        # print(difficulty_num)
        image.alpha_composite(difficulty_parallelograms[difficulty_num], (x - 72, y + 138))
        # 难度标志文字（类型+定级）
        image = draw_text(image, (x + 16, y + 163), f"{difficulty_text} {difficulty_value}", 26, phi_font_path,
                          anchor="mm")
        # 难度标志文件（定值）
        image = draw_text(image, (x + 9, y + 198), f"R: {r}", 38, phi_font_path, anchor="mm")
        # 曲名
        image = draw_text(image, (x + 655, y + 44), f"{music_name}", 32, phi_font_path, anchor="mm")
        # 分数
        image = draw_text(image, (x + 530, y + 131), f"{score}".zfill(7), 37, phi_font_path, anchor="ls")
        # Acc
        accuracy = Decimal((perfect + good * 0.5) / (perfect + good + miss) * 100.0).quantize(Decimal("0.01"),
                                                                                              rounding="ROUND_HALF_UP")
        image = draw_text(image, (x + 738, y + 131), f"{accuracy}%", 27, phi_font_path, anchor="ls")
        # 成绩类型图标
        rank_image = get_score_rank_image(score)
        rank_image = rank_image.resize((115, 115), Image.ANTIALIAS)
        image.alpha_composite(rank_image, (x + 392, y + 80))
        # 成绩细节
        image = draw_text(image, (x + 525, y + 190), "Perfect", 22, phi_font_path, (255, 183, 0, 255), anchor="ls")
        image = draw_text(image, (x + 630, y + 181), f"{perfect}", 22, phi_font_path, anchor="mm")
        image = draw_text(image, (x + 663, y + 190), "Good", 22, phi_font_path, (76, 171, 255, 255), anchor="ls")
        image = draw_text(image, (x + 740, y + 181), f"{good}", 22, phi_font_path, anchor="mm")
        image = draw_text(image, (x + 765, y + 190), "Miss", 22, phi_font_path, (255, 76, 76, 255), anchor="ls")
        image = draw_text(image, (x + 837, y + 181), f"{miss}", 22, phi_font_path, anchor="mm")

        count += 1

    # 玩家名称
    image = draw_text(image, (1430, 330), f"{username}", 68, phi_font_path, anchor="ls")
    # 总R值
    image = draw_text(image, (1430, 430), f"{total_r}", 68, phi_font_path, anchor="ls")
    return image


if __name__ == '__main__':
    b = BombApi("http://43.142.173.63:10443/v1")
    # print(b.get_user_by_name("Taskeren"))
    img = draw_best20(b, "3400cba2-cd86-43d3-ace4-0da1a92481c9")
    img.show("The Record")
