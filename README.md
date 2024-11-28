# MajsoulBot

雀魂三麻bot

---

yolo-v8识别游戏界面 + Mahjong-helper（来自[EndlessCheng](https://github.com/EndlessCheng)） + pyautogui模拟鼠标点击

**本项目仅供学习体验实战使用yolo-v8框架，请勿在有价值的账号上使用，请勿频繁使用，请勿商用开源代码。 因使用本代码带来的掉分、封号等问题，或者因pyautogui点击到错误位置带来的损失，作者概不负责。 错误商用本代码，作者保留追责权利。**

### 2024.11 更新：

+ 雀魂更新了再来一局这个重要的功能，可以极大提升bot的效率和安全性，因此更新了bot的代码来利用这个功能。
+ 减少了对识别UI的视觉模型的依赖，现阶段它实际发挥的作用其实只有识别“立直”按钮，等想到好办法就把它彻底删掉。 
+ 现在bot会在局内使用左侧的按钮来开启除了自动摸切以外的功能。

### 使用方法：

```commandline
pip install -r requirements.txt
python main.py
```

### 数据集：

+ 日麻麻将牌：https://universe.roboflow.com/project-xv49e/mahjong-x5dzz/dataset/2
+ 雀魂UI（自制，规模较小）：https://universe.roboflow.com/majsoulbot/majsoulbot

### 引用的仓库：

+ yolo-v8: https://github.com/ultralytics/ultralytics
+ Mahjong-helper: https://github.com/EndlessCheng/mahjong-helper
+ paddle-ocr: https://github.com/PaddlePaddle/PaddleOCR