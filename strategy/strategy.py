import subprocess
import copy
import os
import re


TRANSLATOR = {'东': '1z', '南': '2z', '西': '3z', '北': '4z', '白': '5z', '发': '6z', '中': '7z',
              '索': 's', '万': 'm', '饼': 'p'}


def sort_hand(hand: list):
    return copy.deepcopy(sorted(hand, key=lambda x: ord(x[1]) * 10 + int(x[0])))


def step(hand: list):
    """
    Discard a tile which maximizes the number of tiles which can form a new set
    :param log: log or not
    :param hand: list (length=14) of tiles (str like '1p', '2z')
    :return: tile: str or None, bool: (str like '1p', '2z') indicating which to discard, click or not
    """
    if len(hand) != 14:
        return hand[0], False
    if '4z' in hand:
        return None, True  # 拔北
    str_hand = ''.join(hand)
    # Author : https://github.com/EndlessCheng
    # Project: https://github.com/EndlessCheng/mahjong-helper
    # Also star him plz!
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mahjong-helper.exe')
    result = subprocess.run([file_path, str_hand], capture_output=True, text=True, encoding='utf-8').stdout
    print(result)
    tenpai = bool('听牌：' in result)
    result = result.replace('切牌', '')  # 可能出现的提示
    best_tile = (result[result.index('切'):])[1:3]
    best_tile = ('' if best_tile[0] == ' ' else best_tile[0]) + (TRANSLATOR[best_tile[1]])
    return best_tile, tenpai


if __name__ == '__main__':
    import random
    CARD = [str(i % 9 + 1) + str(['m', 'p', 's', 'z'][i // 9]) for i in range(34)]
    step(['2p', '2p', '6p', '8p', '4s', '4s', '5s', '5s', '6s', '6s', '7s', '7s', '8s', '9s'])
    # for i in range(10):
    #     hand = []
    #     for j in range(14):
    #         hand.append(CARD[random.randint(0, 10)])
    #     print(sort_hand(hand))
    #     print(step(hand))

