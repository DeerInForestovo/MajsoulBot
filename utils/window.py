import webbrowser
import pygetwindow as gw
from pygetwindow import PyGetWindowException


def get_window():
    # 请不要打开其他叫（或包含）这个名字的窗口，可能导致 bug
    window = gw.getWindowsWithTitle('雀魂麻將')
    return window[0] if window else None


def get_box():
    target_window = get_window()
    window_not_found = target_window is None
    if window_not_found:
        webbrowser.open('steam://rungameid/1329410')  # Majsoul
    while target_window is None:
        target_window = get_window()
    if window_not_found:
        try:
            target_window.activate()
        except PyGetWindowException as e:
            print(e)  # 大部分时候是 pygetwindow.PyGetWindowException: Error code from Windows: 0 - 操作成功完成。
    return (target_window.left, target_window.top,
            target_window.right, target_window.bottom)
