import numpy as np
from ultralytics import YOLO
import supervision as sv
import cv2
import os


def area(xyxy):
    return 0 if xyxy[2] < xyxy[0] or xyxy[3] < xyxy[1] else (xyxy[2] - xyxy[0]) * (xyxy[3] - xyxy[1])


def iou_ratio(xyxy_1, xyxy_2):
    xyxy_u = (
        max(xyxy_1[0], xyxy_2[0]), max(xyxy_1[1], xyxy_2[1]), min(xyxy_1[2], xyxy_2[2]), min(xyxy_1[3], xyxy_2[3]))
    area_u = area(xyxy_u)
    return 0 if area_u == 0 else area_u / (area(xyxy_1) + area(xyxy_2) - area_u)


class Detector:

    def __init__(self):
        weight_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mahjong.pt')
        self.mahjong_model = YOLO(weight_path)
        weight_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'majsoul_UI.pt')
        self.majsoul_model = YOLO(weight_path)

    def detect_tiles(self, image=None):
        test_mode = False
        if image is None:  # test
            test_mode = True
            image = cv2.imread('game.jpg')

        # inference
        height, width = len(image), len(image[0])
        left, right, top, bottom = width//10, width//10*9, height//4*3, height
        # left, right, top, bottom = 0, width, 0, height
        image = image[top: bottom, left: right]  # hand region
        results = self.mahjong_model.predict(source=image, imgsz=(224, 1024), augment=True)

        # get result
        detections = sv.Detections.from_ultralytics(results[0])
        xyxy_ = detections.xyxy.tolist()
        confidence_ = np.array(detections.confidence).tolist()
        tiles_ = detections.data['class_name'].tolist()

        if len(tiles_):
            # what is a tile looks like?
            feature_funcs = [
                lambda a: a[2] - a[0],  # width
                lambda a: a[3] - a[1],  # height
                lambda a: a[3] + a[1],  # sum_y
                area
            ]
            feature = [np.median([func(a) for a in xyxy_]) for func in feature_funcs]
            feature_len = len(feature)

            def similar(a, b):
                return abs(abs(a - b) / max(a, b)) < 0.2

            i = 0
            while i < len(xyxy_):
                tag = False
                for f in range(feature_len):
                    if not similar(feature_funcs[f](xyxy_[i]), feature[f]):
                        tag = True
                        break
                if tag:
                    print('Detector: Wrong tile removed')
                    test_mode = True  # save the image
                    xyxy_.pop(i)
                    confidence_.pop(i)
                    tiles_.pop(i)
                else:
                    i += 1

            if len(xyxy_):
                # 选出每个位置confidence最高的牌
                xyxy = [[None] * 4] * 160
                tiles = [None] * 160
                confidence = [-1] * 160
                tile_width = np.median([a[2] - a[0] for a in xyxy_])
                left_margin = xyxy_[np.argmin(xyxy_, axis=0)[0]][0]
                pos_list = []
                for i in range(len(tiles_)):
                    pos = int(round(float(xyxy_[i][0] - left_margin) / tile_width))
                    pos_list.append(pos)
                    if confidence[pos] < confidence_[i]:
                        confidence[pos] = confidence_[i]
                        xyxy[pos] = xyxy_[i]
                        tiles[pos] = tiles_[i]
                print(pos_list)
                for i in range(1, 12):
                    if tiles[i - 1] == tiles[i + 1] and tiles[i - 1] is not None and tiles[i] is None:
                        tiles[i] = tiles[i - 1]
                        xyxy[i] = [xyxy[i - 1][2], xyxy[i - 1][1], xyxy[i + 1][0], xyxy[i + 1][3]]
                        print('Detector: special fix tile[%d] = %s' % (i, tiles[i]))
                        test_mode = True
                        # 连续的三张白可能会识别不出中间那张
                xyxy = list(filter(lambda x: x[0] is not None, xyxy))
                tiles = list(filter(lambda x: x is not None, tiles))
                for i in range(len(xyxy)):
                    xyxy[i][0] += left
                    xyxy[i][1] += top
                    xyxy[i][2] += left
                    xyxy[i][3] += top
            else:
                xyxy = []
                tiles = []
        else:
            xyxy = []
            tiles = []

        # test
        if test_mode or len(tiles) not in [0, 1, 2, 13, 14]:
            bounding_box_annotator = sv.BoundingBoxAnnotator()
            label_annotator = sv.LabelAnnotator()
            labels = [self.mahjong_model.model.names[class_id] for class_id in detections.class_id]
            annotated_image = bounding_box_annotator.annotate(scene=image, detections=detections)
            annotated_image = label_annotator.annotate(scene=annotated_image, detections=detections, labels=labels)
            cv2.imwrite('last_abnormal_detection.jpg', annotated_image)

        return xyxy, tiles

    def detect_frame(self, image=None):
        test_mode = False
        if image is None:  # test
            test_mode = True
            image = cv2.imread('game.jpg')

        # inference
        height, width = len(image), len(image[0])
        left, right, top, bottom = 0, width, 0, height
        image = image[top: bottom, left: right]
        results = self.majsoul_model.predict(source=image, augment=True)

        # get result
        detections = sv.Detections.from_ultralytics(results[0])
        xyxy_ = detections.xyxy.tolist()
        confidence_ = np.array(detections.confidence).tolist()
        buttons_ = detections.data['class_name'].tolist()

        # 如果有重合区域被识别为不同的类，只保留confidence最高的预测
        # 和识别手牌的方法实现不同，是因为手牌可以利用（也必须利用，为了复原太难检测的白暗刻）相对位置信息
        xyxy = []
        buttons = []
        if len(buttons_):
            for i in range(len(buttons_)):
                tag = True
                for j in range(len(buttons_)):
                    if i != j and iou_ratio(xyxy_[i], xyxy_[j]) > 0.5 and confidence_[i] < confidence_[j]:
                        tag = False
                        break
                if tag:
                    xyxy.append(xyxy_[i])
                    buttons.append(buttons_[i])
            for i in range(len(xyxy)):
                xyxy[i][0] += left
                xyxy[i][1] += top
                xyxy[i][2] += left
                xyxy[i][3] += top

        # test
        if test_mode:
            bounding_box_annotator = sv.BoundingBoxAnnotator()
            label_annotator = sv.LabelAnnotator()
            labels = [self.majsoul_model.model.names[class_id] for class_id in detections.class_id]
            annotated_image = bounding_box_annotator.annotate(scene=image, detections=detections)
            annotated_image = label_annotator.annotate(scene=annotated_image, detections=detections, labels=labels)
            cv2.imwrite('detection.jpg', annotated_image)

        return xyxy, buttons


if __name__ == '__main__':
    detector = Detector()
    # xyxy, tiles = detector.detect_tiles()
    # print('%d tiles' % len(tiles))
    # for x, t in zip(xyxy, tiles):
    #     print(t + ' ' + str(x))
    print(detector.detect_frame())
