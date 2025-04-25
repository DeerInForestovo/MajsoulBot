import pyautogui
from time import sleep


class MyClick:

    def __init__(self):
        self.top_left_corner = (0, 0)

    def set_top_left_corner(self, box):
        self.top_left_corner = (box[0], box[1])

    def click(self, box, click=True, center=True) -> None:
        if center:
            x, y = (box[0] + box[2]) // 2 + self.top_left_corner[0], (box[1] + box[3]) // 2 + self.top_left_corner[1]
        else:  # click top-left corner
            x, y = box[0] + self.top_left_corner[0], box[1] + self.top_left_corner[1]
        pyautogui.moveTo(x, y)
        if click:
            print('click x = %d, y = %d' % (x, y))
            pyautogui.click()
            sleep(0.1)
