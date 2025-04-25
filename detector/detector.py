import numpy as np
from ultralytics import YOLO
import os
import torch


def area(xyxy):
    return 0 if xyxy[2] < xyxy[0] or xyxy[3] < xyxy[1] else (xyxy[2] - xyxy[0]) * (xyxy[3] - xyxy[1])


def iou_ratio(xyxy_1, xyxy_2):
    xyxy_u = (
        max(xyxy_1[0], xyxy_2[0]), max(xyxy_1[1], xyxy_2[1]), min(xyxy_1[2], xyxy_2[2]), min(xyxy_1[3], xyxy_2[3]))
    area_u = area(xyxy_u)
    return 0 if area_u == 0 else area_u / (area(xyxy_1) + area(xyxy_2) - area_u)


class Detector:

    def __init__(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        mahjong_model_path = os.path.join(base_path, 'mahjong.pt')
        majsoul_model_path = os.path.join(base_path, 'majsoul_UI.pt')

        self.mahjong_model = YOLO(mahjong_model_path)
        self.majsoul_model = YOLO(majsoul_model_path)

        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f'device: {device}')
        self.mahjong_model = self.mahjong_model.to(device)
        self.majsoul_model = self.majsoul_model.to(device)

    def detect_tiles(self, image=None):
        height, width = len(image), len(image[0])
        left, right, top, bottom = width // 10, width // 10 * 9, height // 4 * 3, height
        cropped_image = image[top: bottom, left: right]

        results = self.mahjong_model.predict(source=cropped_image, imgsz=(224, 1024), augment=True)
        result = results[0]
        boxes = result.boxes.xyxy.cpu().numpy()
        confidences = result.boxes.conf.cpu().numpy()
        class_ids = result.boxes.cls.cpu().numpy()

        class_names = [result.names[int(cls_id)] for cls_id in class_ids]
        if not class_names:
            return []

        def area(bbox):
            return (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])

        def is_similar(a, b):
            return abs(abs(a - b) / max(a, b)) < 0.2

        features = [
            lambda b: b[2] - b[0],  # width
            lambda b: b[3] - b[1],  # height
            lambda b: b[3] + b[1],  # sum_y
            area
        ]
        medians = [np.median([f(b) for b in boxes]) for f in features]

        filtered_boxes, filtered_confidences, filtered_classes = [], [], []
        for i in range(len(boxes)):
            if all(is_similar(features[f](boxes[i]), medians[f]) for f in range(len(features))):
                filtered_boxes.append(boxes[i])
                filtered_confidences.append(confidences[i])
                filtered_classes.append(class_names[i])

        if not filtered_boxes:
            return []

        result_data = [None] * 160
        median_tile_width = np.median([box[2] - box[0] for box in filtered_boxes])
        leftmost = min(box[0] for box in filtered_boxes)

        for i in range(len(filtered_boxes)):
            position = int(round((filtered_boxes[i][0] - leftmost) / median_tile_width))
            if result_data[position] is None or result_data[position]["confidence"] < filtered_confidences[i]:
                result_data[position] = {
                    "bbox": filtered_boxes[i],
                    "label": filtered_classes[i],
                    "confidence": filtered_confidences[i]
                }

        # 修复白暗刻中间丢失
        for i in range(1, 12):
            prev = result_data[i - 1]
            next_ = result_data[i + 1]
            if prev and next_ and prev["label"] == next_["label"] and result_data[i] is None:
                result_data[i] = {
                    "bbox": [
                        prev["bbox"][2],
                        prev["bbox"][1],
                        next_["bbox"][0],
                        next_["bbox"][3]
                    ],
                    "label": prev["label"],
                    "confidence": min(prev["confidence"], next_["confidence"])
                }

        # 补上偏移量
        final_result = []
        for entry in result_data:
            if entry:
                x1, y1, x2, y2 = entry["bbox"]
                entry["bbox"] = [x1 + left, y1 + top, x2 + left, y2 + top]
                final_result.append(entry)

        return final_result
    
    def detect_frame(self, image=None):
        height, width = len(image), len(image[0])
        left, right, top, bottom = 0, width, 0, height
        cropped_image = image[top: bottom, left: right]

        results = self.majsoul_model.predict(source=cropped_image, augment=True)
        result = results[0]

        boxes = result.boxes.xyxy.cpu().numpy()
        confidences = result.boxes.conf.cpu().numpy()
        class_ids = result.boxes.cls.cpu().numpy()

        class_names = [result.names[int(cls_id)] for cls_id in class_ids]
        if not class_names:
            return []

        filtered_results = []
        for i in range(len(class_names)):
            keep = True
            for j in range(len(class_names)):
                if i != j and iou_ratio(boxes[i], boxes[j]) > 0.5 and confidences[i] < confidences[j]:
                    keep = False
                    break
            if keep:
                x1, y1, x2, y2 = boxes[i]
                bbox = [x1 + left, y1 + top, x2 + left, y2 + top]
                filtered_results.append({
                    "bbox": bbox,
                    "label": class_names[i],
                    "confidence": confidences[i]
                })

        return filtered_results

