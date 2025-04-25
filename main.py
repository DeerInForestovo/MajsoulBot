import cv2
from PIL import ImageGrab
import numpy as np
from time import time

from utils.click import MyClick
from utils.window import get_box
from detector.detector import Detector
from strategy.strategy import step

MAX_INTERNAL = 3.5  # 几秒检测一次画面
my_click = MyClick()
my_detector = Detector()


def only_one_queren(buttons):
    # 只保留 '确认' 中 y 最小（最靠上）的那个
    queren_buttons = [btn for btn in buttons if btn["label"] == "queren"]

    if queren_buttons:
        # 找到 bbox 中 y2 最大的那个
        lowest_queren = min(queren_buttons, key=lambda b: b["bbox"][3])
        filtered_buttons = [btn for btn in buttons if btn["label"] != "queren"]
        filtered_buttons.append(lowest_queren)
        return filtered_buttons
    else:
        return buttons


def press_button(buttons, label):
    for button in buttons:
        if button['label'] == label:
            my_click.click(button['bbox'])
            return True
    print('not found: ', label)
    return False


def press_toolbar(buttons, image):
    for button in buttons:
        if button['label'] == 'toolbar':
            x1, y1, x2, y2 = button['bbox']
            toolbar_height = y2 - y1
            toolbar_width = x2 - x1

            unit = toolbar_height / 252  # 基于 12:28 的比例划分单位高度
            gap = unit * 12
            btn_size = unit * 28

            for i in [1, 2, 4]:  # 尝试点击按钮
                top = int(y1 + gap + i * (btn_size + gap))
                bottom = int(top + btn_size)
                left = int(x1 + gap)
                right = int(x2 - gap)

                cropped_image = image[top:bottom, left:right]
                mean_color = cv2.mean(cropped_image)[:3]
                b, g, r = mean_color

                if not (g > r and g > b):
                    my_click.click((left, top, right, bottom))



if __name__ == '__main__':
    last_infer_time = -10000
    while True:
        now_time = time()
        if now_time - last_infer_time <= MAX_INTERNAL:
            continue
        last_infer_time = now_time

        # 获取游戏界面范围
        box = get_box()
        my_click.set_top_left_corner(box)

        # 获取游戏界面
        image = np.array(ImageGrab.grab(box))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # 用视觉模型识别游戏界面
        tiles = my_detector.detect_tiles(image)
        buttons = my_detector.detect_frame(image)

        # 过滤按钮
        button_filters = [
            only_one_queren
        ]
        for filter in button_filters:
            buttons = filter(buttons)
        button_labels = [btn['label'] for btn in buttons]

        # 匹配中
        if 'pipei_1' in button_labels or 'pipei_2' in button_labels:
            print("In queue")
            continue

        # 总是会按下的按钮
        # 其中，confirm是两小局之间的蓝色确认按钮，queren是大局之间的黄色按钮
        always_press_group = [
            ['match', 'silver', '3p-east', 'zailaiyichang', 'zimo', 'he', 'babei'],
            ['queren', 'confirm']  # 再来一场优先级高于确认
        ]
        is_pressed = False
        for always_press in always_press_group:
            for label in always_press:
                if press_button(buttons, label):
                    is_pressed = True
                    break
            if is_pressed:
                break
        if is_pressed:
            print("Pressed a button")
            continue

        # 处于一局游戏内
        if len(tiles) >= 13:
            press_toolbar(buttons, image)
            if len(tiles) == 13:
                print("In game, not my turn")
                press_button(buttons, 'tiaoguo')
            elif len(tiles) == 14:
                print("In game, discard")
                tile, button = step([t['label'] for t in tiles])
                press_button(buttons, button)
                press_button(tiles, tile)
                my_click.click((0, 0, box[2] - box[0], box[3] - box[1]), click=False)

        # 未知情况，尝试点击屏幕中间
        elif len(tiles) < 3:
            print("Where am I?")
            for i in range(4):
                my_click.click((0, 0, box[2] - box[0], box[3] - box[1]))

