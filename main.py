import cv2
import pyscreenshot
import numpy as np
from time import time, sleep

from utils.click import MyClick
from utils.window import get_box
from detector.detector import Detector
from strategy.strategy import step, sort_hand

MAX_QUEUE_TIME = 30  # 超过30秒重新开始匹配

if __name__ == '__main__':
    my_click = MyClick()
    my_detector = Detector()
    my_step = step

    waiting = False
    queuing = False
    confirming = False
    wait_time = None
    queue_time = None
    confirm_time = None
    while True:
        # get box
        box = get_box()
        my_click.set_top_left_corner(box)

        # get and detect game frame
        image = np.array(pyscreenshot.grab(box))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        xyxy_tiles, tiles = my_detector.detect_tiles(image)
        xyxy_buttons, buttons = my_detector.detect_frame(image)

        print('############################################')
        print(str(len(tiles)) + ' tiles')
        print(sort_hand(tiles))
        print(buttons)
        print('############################################')

        if '3p-east' in buttons:
            waiting = False
            confirming = False
            if queuing and time() - queue_time < MAX_QUEUE_TIME:
                print('queuing')
                continue
            if len(buttons) != 1:
                print('inference again')
                continue
            print('click 3p-east')
            my_click.click(xyxy_buttons[buttons.index('3p-east')])
            queuing = True
            queue_time = time()
        else:
            waiting = False
            queuing = False
            if 'confirm' in buttons:
                # 有倒计时的确定就让其自动消失，连续检测到说明是没有倒计时的，此时狂点
                print('confirm detected')
                if not confirming:
                    confirming = True
                    confirm_time = time()
                elif time() - confirm_time > 5:
                    confirming = False
                    print('click confirm')
                    box = xyxy_buttons[buttons.index('confirm')]
                    # 点左上角……不然bot就要帮你抽十连了
                    box[2] -= (box[2] - box[0]) // 2
                    box[3] -= (box[3] - box[1]) // 2
                    for i in range(30):
                        my_click.click(box)
                        sleep(0.1)
            else:
                confirming = False
                if 'match' in buttons:
                    print('click match')
                    my_click.click(xyxy_buttons[buttons.index('match')])
                elif 'silver' in buttons:
                    print('click silver')
                    my_click.click(xyxy_buttons[buttons.index('silver')])
                elif 'zimo' in buttons:
                    print('click zimo')
                    my_click.click(xyxy_buttons[buttons.index('zimo')])
                elif 'he' in buttons:
                    print('click he')
                    my_click.click(xyxy_buttons[buttons.index('he')])
                # elif 'babei' in buttons:
                #     print('click babei')
                #     my_click.click(xyxy_buttons[buttons.index('babei')])
                elif ('chi' in buttons or 'peng' in buttons or 'gang' in buttons) and \
                        'lizhi' not in buttons and 'babei' not in buttons:
                    if 'chi' in buttons:
                        print('refuse chi')
                    if 'peng' in buttons:
                        print('refuse peng')
                    if 'gang' in buttons:
                        print('refuse gang')
                    if 'tiaoguo' in buttons:
                        print('click tiaoguo')
                        my_click.click(xyxy_buttons[buttons.index('tiaoguo')])
                    else:
                        print('chi/peng/gang found, but tiaoguo not found')
                elif len(tiles) == 14:
                    print('discard')
                    tile, button = my_step(tiles)
                    print('tile = %s, button = %s' % (tile, button))
                    if button in buttons:
                        my_click.click(xyxy_buttons[buttons.index(button)])
                        sleep(0.3)
                    elif button:
                        print('button not found')
                    if tile in tiles:
                        my_click.click(xyxy_tiles[tiles.index(tile)])
                    elif tile:
                        print('tile not found')
                else:
                    print('waiting')
                    if not waiting:
                        waiting = True
                        wait_time = time()
                    elif time() - wait_time > MAX_QUEUE_TIME:
                        # 很久没有检测到认识的目标了，应该是卡在了领取奖励页面
                        waiting = False
                        for i in range(7):
                            my_click.click((0, 0, box[2] - box[0], box[3] - box[1]))
                            sleep(0.05)

        # 将鼠标挪到中间，避免遮挡目标
        if not waiting:
            my_click.click((0, 0, box[2] - box[0], box[3] - box[1]), click=False)
