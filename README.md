# MajsoulBot

雀魂三麻bot

yolov8识别游戏界面 + 不知道什么原理的AI（来自[EndlessCheng](https://github.com/EndlessCheng)） + pyautogui模拟鼠标点击

**警告！！！警告！！！警告！！！** 本项目仅供学习体验实战使用yolov8框架，请勿在有价值的账号上使用，请勿频繁使用，请勿商用开源代码。

因使用本代码带来的掉分、封号等问题，或者因pyautogui点击到错误位置带来的损失，作者概不负责。

错误商用本代码，作者保留追责权利，或至少画个圈圈诅咒你。

使用方法：

1. 正确安装yolov8（参考[文档](https://docs.ultralytics.com/quickstart/#install-ultralytics)，需要先手动装pytorch再装yolo
2. 游戏分辨率应为1600*1200，也可以自行修改main.py中的全局变量（截图放进画图软件，看要点的位置和左上角的距离）
3. 工作流程为：在首页开启脚本，自动匹配银之间三人东对局，自动进行对局（只看当前手牌信息，打银之间够用），结束后自动开启下一把
4. 游戏过程中，不要挪动窗口，因为截图位置是固定的。同理想要避免鼠标被脚本一直抢（比如你想关掉脚本的时候）将窗口挪开或切屏即可

数据集：

+ 日麻麻将牌：https://universe.roboflow.com/project-xv49e/mahjong-x5dzz/dataset/2

引用的仓库：

+ yolov8：https://github.com/ultralytics/ultralytics

+ Mahjong-helper：https://github.com/EndlessCheng/mahjong-helper

