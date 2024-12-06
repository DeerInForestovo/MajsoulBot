import cv2
import pyscreenshot
import numpy as np
from time import time, sleep
import colorama
from colorama import Fore
import datetime

from utils.click import MyClick
from utils.window import get_box
from detector.detector import Detector
from strategy.strategy import step

MAX_QUEUE_TIME = 30  # 超过30秒重新开始匹配
MAX_WAIT_TIME = 15

if __name__ == '__main__':
    colorama.init()
    print(Fore.WHITE)
    my_click = MyClick()
    my_detector = Detector()
    my_step = step

    waiting = False
    queuing = False
    wait_time = None
    queue_time = None

    while True:
        # 获取游戏界面范围
        box = get_box()
        my_click.set_top_left_corner(box)

        # 获取游戏界面
        image = np.array(pyscreenshot.grab(box))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # 用视觉模型识别游戏界面
        xyxy_tiles, tiles = my_detector.detect_tiles(image)
        xyxy_buttons, buttons = my_detector.detect_frame(image)
        char_dict = my_detector.detect_characters(image)

        print(char_dict.keys())

        if '3p-east' in buttons or 'match' in buttons or 'silver' in buttons:  # 匹配中
            print(Fore.GREEN + f'[{datetime.datetime.now()}]: 匹配中' + Fore.WHITE)
            waiting = False
            if queuing and time() - queue_time < MAX_QUEUE_TIME:
                continue
            if '3p-east' in buttons:
                my_click.click(xyxy_buttons[buttons.index('3p-east')])
                queuing = True
                queue_time = time()
            elif 'match' in buttons:
                my_click.click(xyxy_buttons[buttons.index('match')])
            elif 'silver' in buttons:
                my_click.click(xyxy_buttons[buttons.index('silver')])

        elif 'zhongju' in char_dict.keys() or 'queren' in char_dict.keys():  # 终局界面
            print(Fore.GREEN + f'[{datetime.datetime.now()}]: 终局界面' + Fore.WHITE)
            waiting = queuing = False
            if '2queren' in char_dict.keys():  # 有两个确认，即“再来一场”的确认窗口，此时点确认
                if 'queren' in char_dict.keys():
                    my_click.click(char_dict['queren'])
            elif 'zailaiyichang' in char_dict.keys():  # 有再来一场且没有两个确认，此时点再来一场
                my_click.click(char_dict['zailaiyichang'])
            elif 'queren' in char_dict.keys():  # 只有一个确认，应该是展示得分、奖励等界面，此时点击确认
                my_click.click(char_dict['queren'])
            else:  # 只有终局，没有其他文字，应该是活动奖励界面，这个界面没有确认按钮，此时点一下屏幕中间
                my_click.click((0, 0, box[2] - box[0], box[3] - box[1]))

        else:  # 游戏中（或未知界面）
            print(Fore.GREEN + f'[{datetime.datetime.now()}]: 游戏中' + Fore.WHITE)
            # 尝试按左侧按钮
            if 'lhmqb' in char_dict.keys():
                xyxy = char_dict['lhmqb']
                for x in [0, 1, 2, 4]:  # 尝试点下五个按钮中的第x个
                    height = (xyxy[3] - xyxy[1]) // 5
                    left, top, right, bottom = (int(xyxy[0]), int(xyxy[1] + x * height),
                                                int(xyxy[2]), int(xyxy[1] + (x + 1) * height))
                    cropped_image = image[top: bottom, left: right]
                    mean_color = cv2.mean(cropped_image)[:3]
                    b, g, r = mean_color
                    if not (g > r and g > b and g - r > 20):  # 如果是按下状态，绿色应该占主导
                        my_click.click((left, top, right, bottom))

            # 处理游戏内容
            p_waiting = waiting
            waiting = False  # 如果以下一条触发，waiting就应该取消，否则就应该保持。这里提前取消
            if 'zimo' in buttons:
                my_click.click(xyxy_buttons[buttons.index('zimo')])
            elif 'he' in buttons:
                my_click.click(xyxy_buttons[buttons.index('he')])
            elif 'babei' in buttons:
                my_click.click(xyxy_buttons[buttons.index('babei')])
            elif ('chi' in buttons or 'peng' in buttons or 'gang' in buttons) and \
                    'lizhi' not in buttons and 'babei' not in buttons:  # 副露的选择：bot选择永远不副露
                if 'chi' in buttons:
                    pass
                if 'peng' in buttons:
                    pass
                if 'gang' in buttons:
                    pass
                if 'tiaoguo' in buttons:
                    my_click.click(xyxy_buttons[buttons.index('tiaoguo')])
                else:  # 有按钮但没检测到跳过
                    pass
            elif len(tiles) == 14:  # 切牌，拔北或立直
                tile, button = my_step(tiles)
                # print('tile = %s, button = %s' % (tile, button))
                if button in buttons:  # 拔北或立直
                    my_click.click(xyxy_buttons[buttons.index(button)])
                    sleep(0.3)
                elif button:  # 要求按钮但没检测到
                    pass
                if tile in tiles:
                    my_click.click(xyxy_tiles[tiles.index(tile)])
                elif tile:  # 没检测到要求切的牌
                    pass
            else:  # 等待中，或处于未知界面
                waiting = p_waiting  # 以上一条都没有触发，执行到这一行，那么waiting应该不变（取回原状态）
                if not waiting:
                    print('begin wait.', wait_time)
                    waiting = True
                    wait_time = time()
                elif time() - wait_time > MAX_WAIT_TIME:
                    # 很久没有检测到认识的目标了，应该是卡在了领取奖励页面
                    # 尝试点击屏幕中心
                    print('wait long.', time())
                    waiting = False
                    for i in range(7):
                        my_click.click((0, 0, box[2] - box[0], box[3] - box[1]))
                        sleep(0.05)

        # 将鼠标挪到中间，避免遮挡目标
        my_click.click((0, 0, box[2] - box[0], box[3] - box[1]), click=False)

