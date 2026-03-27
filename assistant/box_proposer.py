import cv2
import numpy as np
from core.annotation import AnnotationItem
from .edge_detector import detect_edges
from .color_segmenter import segment_color
from .saliency_detector import detect_saliency
from .mser_detector import detect_mser
from .otsu_detector import detect_otsu
from .grabcut_detector import detect_grabcut

def non_max_suppression_fast(boxes, overlapThresh):
    """快速 NMS 非极大值抑制"""
    if len(boxes) == 0:
        return []

    if boxes.dtype.kind == "i":
        boxes = boxes.astype("float")

    pick = []
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]

    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(y2)

    while len(idxs) > 0:
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])

        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        overlap = (w * h) / area[idxs[:last]]

        idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > overlapThresh)[0])))

    return boxes[pick].astype("int")

def propose_boxes(image, mode='edge', min_area=400, nms_threshold=0.3, **kwargs):
    """
    根据选择的模式返回归一化标注坐标
    """
    img_h, img_w = image.shape[:2]
    
    if mode == 'edge':
        t1 = kwargs.get('canny_t1', 50)
        t2 = kwargs.get('canny_t2', 150)
        raw_boxes = detect_edges(image, threshold1=t1, threshold2=t2)
    elif mode == 'color':
        k = kwargs.get('kmeans_k', 3)
        raw_boxes = segment_color(image, k=k)
    elif mode == 'saliency':
        raw_boxes = detect_saliency(image)
    elif mode == 'mser':
        delta = kwargs.get('mser_delta', 5)
        raw_boxes = detect_mser(image, delta=delta)
    elif mode == 'otsu':
        blur_size = kwargs.get('otsu_blur', 5)
        raw_boxes = detect_otsu(image, blur_size=blur_size)
    elif mode == 'grabcut':
        iter_count = kwargs.get('grabcut_iter', 5)
        margin = kwargs.get('grabcut_margin', 10)
        raw_boxes = detect_grabcut(image, iter_count=iter_count, margin=margin)
    else:
        raw_boxes = []

    # 过滤小面积和计算 [x1, y1, x2, y2]
    filtered_boxes = []
    for (x, y, w, h) in raw_boxes:
        if w * h > min_area:
            filtered_boxes.append([x, y, x + w, y + h])

    if not filtered_boxes:
        return []

    # NMS
    filtered_boxes = np.array(filtered_boxes)
    nms_boxes = non_max_suppression_fast(filtered_boxes, nms_threshold)

    annotations = []
    for (x1, y1, x2, y2) in nms_boxes:
        # 转为中心坐标归一化
        w = (x2 - x1) / img_w
        h = (y2 - y1) / img_h
        x_c = (x1 + x2) / 2 / img_w
        y_c = (y1 + y2) / 2 / img_h
        
        # 默认使用 class_id = 0
        annotations.append(AnnotationItem(0, x_c, y_c, w, h))
        
    return annotations
