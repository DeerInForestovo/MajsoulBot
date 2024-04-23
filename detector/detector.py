import numpy as np
from ultralytics import YOLO
import supervision as sv
import cv2


class Detector:

    def __init__(self, weight: str):
        self.model = YOLO(weight)

    def detect(self, image=None):
        test_mode = False
        if image is None:  # test
            test_mode = True
            image = cv2.imread('game.jpg')
        height, width = len(image), len(image[0])
        left, right, top, bottom = width//10, width//10*9, height//4*3, height
        # left, right, top, bottom = 0, width, 0, height
        image = image[top: bottom, left: right]  # hand region
        results = self.model.predict(source=image, imgsz=(224, 1024), augment=True)
        detections = sv.Detections.from_ultralytics(results[0])
        xyxy_ = detections.xyxy.tolist()
        confidence_ = np.array(detections.confidence).tolist()
        tiles_ = detections.data['class_name'].tolist()
        xyxy = []
        tiles = []
        if len(tiles_):
            xyxy = [[None] * 4] * 160
            tiles = [None] * 160
            confidence = [-1] * 160
            tile_width = xyxy_[0][2] - xyxy_[0][0]
            left_margin = xyxy_[np.argmin(detections.xyxy, axis=0)[0]][0]
            for i in range(len(tiles_)):
                pos = int(round(float(xyxy_[i][0] - left_margin) / tile_width))
                if confidence[pos] < confidence_[i]:
                    confidence[pos] = confidence_[i]
                    xyxy[pos] = xyxy_[i]
                    tiles[pos] = tiles_[i]
            for i in range(1, 14):
                if tiles[i-1] == tiles[i+1] and tiles[i-1] is not None and tiles[i] is None:
                    tiles[i] = tiles[i-1]
                    xyxy[i] = [xyxy[i-1][2], xyxy[i-1][1], xyxy[i+1][0], xyxy[i+1][3]]
                    print('Warning: Detector special fix tile[%d] = %s' % (i, tiles[i]))
                    # 连续的三张白可能会识别不出中间那张
            xyxy = list(filter(lambda x: x[0] is not None, xyxy))
            tiles = list(filter(lambda x: x is not None, tiles))
            for i in range(len(xyxy)):
                xyxy[i][0] += left
                xyxy[i][1] += top
                xyxy[i][2] += left
                xyxy[i][3] += top
        if test_mode:
            bounding_box_annotator = sv.BoundingBoxAnnotator()
            label_annotator = sv.LabelAnnotator()
            labels = [self.model.model.names[class_id] for class_id in detections.class_id]
            annotated_image = bounding_box_annotator.annotate(scene=image, detections=detections)
            annotated_image = label_annotator.annotate(scene=annotated_image, detections=detections, labels=labels)
            cv2.imwrite('detection.jpg', annotated_image)
        return xyxy, tiles


if __name__ == '__main__':
    detector = Detector('best.pt')
    xyxy, tiles = detector.detect()
    print('%d tiles' % len(tiles))
    for x, t in zip(xyxy, tiles):
        print(t + ' ' + str(x))

