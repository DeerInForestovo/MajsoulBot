# MajsoulBot

雀魂三麻bot，门清即立低段位刷好感刷活动用。

---

[YOLO](https://github.com/ultralytics/ultralytics) + [Mahjong-helper](https://github.com/EndlessCheng/mahjong-helper) + pyautogui

**本项目仅供学习体验实战使用yolo-v11n模型，请勿在有价值的账号上使用，请勿频繁使用，请勿商用开源代码。 因使用本代码带来的掉分、封号等问题，或者因pyautogui点击到错误位置带来的损失，作者概不负责。 错误商用本代码，作者保留追责权利。**

### 2025.4 更新：

+ 完全重写逻辑：依赖视觉模型尽可能识别画面中的元素，对按钮分配优先级与实现handler，删除了ocr模型和状态机
+ 这个版本在降低算力消耗和提升稳定性上应该都有不错的进步
+ 如果之前安装过本仓库，可以删掉原本的 paddle OCR 部分
+ 如果想启用 GPU ，将依赖里的 torch 三件套换成 GPU 版本即可，不用修改代码

### 使用方法：

使用 steam 雀魂客户端，登录账号，确保有打银之间-三人东的资格。窗口大小设置为 1024x768 （其他窗口大小也可以，这个是算力和清晰度比较平衡的设置），确保雀魂窗口完整露出，不被其他窗口遮挡。

```commandline
pip install -r requirements.txt
python main.py
```

### 数据集：

+ 日麻麻将牌：https://universe.roboflow.com/project-xv49e/mahjong-x5dzz/dataset/2
+ 雀魂UI（自制）：https://universe.roboflow.com/majsoulbot/majsoulbot

### 引用的仓库：

+ YOLO-v11n: https://github.com/ultralytics/ultralytics
+ Mahjong-helper: https://github.com/EndlessCheng/mahjong-helper
