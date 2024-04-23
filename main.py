import cv2
from detector.detector import Detector
from strategy.strategy import step, sort_hand
import pygetwindow as gw
import pyscreenshot
import numpy as np
from time import time, sleep
import pyautogui


IDLE_TIME = 20  # 超过这个时间认为需要重新匹配游戏

# 屏幕分辨率：2880*1800
# 游戏分辨率：1600*1200
IDLE = (400, 400)  # 挪开鼠标避免印象截图
DUAN_WEI_CHANG = (1102, 484)
YIN_ZHI_JIAN = (1128, 700)
SAN_REN_DONG = (1135, 830)
QUE_DING = (1432, 1040)
OPERATION = (857, 897)  # 拔北或立直
HE_PAI = (35, 680)
TIAO_GUO = (36, 740)


class MyClick:

    def __init__(self, left_corner: (int, int)):
        self.left_corner = left_corner

    def click(self, position: (int, int), c=True) -> None:
        x, y = position[0] + self.left_corner[0], position[1] + self.left_corner[1]
        print('click x = %d, y = %d' % (x, y))
        pyautogui.moveTo(x, y)
        if c:
            pyautogui.click()


if __name__ == '__main__':

    # get window
    all_windows = gw.getAllTitles()
    target_window_title = '雀魂麻將'
    target_window = None
    for title in all_windows:
        if target_window_title in title:
            target_window = gw.getWindowsWithTitle(title)[0]
            break
    if target_window:
        target_window.activate()
        bounding_box = (target_window.left, target_window.top,
                        target_window.right, target_window.bottom)

        my_click = MyClick((target_window.left, target_window.top))
        my_detector = Detector('detector/best.pt')
        my_step = step

        waiting_from = time() - IDLE_TIME
        waiting = True
        queuing = False
        while True:
            sleep(1.5)
            # get and detect game frame
            image = np.array(pyscreenshot.grab(bounding_box))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            xyxy, tiles = my_detector.detect(image)
            print('detect result:')
            print(sort_hand(tiles))

            # state-machine
            if len(tiles) < 13:
                if queuing:  # 匹配中
                    print('queuing')
                    continue
                if waiting and time() - waiting_from > IDLE_TIME:  # 匹配游戏
                    print('begin to queue')
                    for _ in range(20):
                        my_click.click(QUE_DING)  # 点确定（无倒计时）
                        sleep(0.1)
                    sleep(8)
                    my_click.click(DUAN_WEI_CHANG)
                    sleep(0.8)
                    my_click.click(YIN_ZHI_JIAN)
                    sleep(0.8)
                    my_click.click(SAN_REN_DONG)
                    waiting = False
                    queuing = True  # 直到模型识别到麻将牌，结束匹配
                elif not waiting:  # 开始等待
                    print('begin to wait')
                    waiting = True
                    waiting_from = time()
            else:  # 在游戏中
                if waiting or queuing:
                    # 刚进入游戏
                    waiting = False
                    queuing = False
                    my_click.click(HE_PAI)  # 点自动和牌
                    sleep(0.06)
                    my_click.click(TIAO_GUO)  # 点不吃碰杠
                    sleep(0.06)
                my_click.click(QUE_DING)  # 点确定（无倒计时）以防误判
                sleep(0.1)
                if len(tiles) == 13:  # 空闲或等待鸣牌
                    print('waiting during game')
                else:  # 等待出牌
                    print('play')
                    best_tile, click = my_step(tiles)
                    if click:
                        print('click')
                        my_click.click(OPERATION)  # 拔北或立直
                        sleep(0.12)
                    if best_tile is not None:
                        try:
                            index = tiles.index(best_tile)
                        except ValueError as e:
                            index = 0
                        print('discard ' + tiles[index])
                        my_click.click(((xyxy[index][0] + xyxy[index][2]) // 2,
                                        (xyxy[index][1] + xyxy[index][3]) // 2))
                my_click.click(IDLE, False)

