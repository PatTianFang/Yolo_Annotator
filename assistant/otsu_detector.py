import cv2
import numpy as np

def detect_otsu(image, blur_size=5):
    """
    基于大津法 (Otsu's method) 的全局自适应阈值分割
    同时检测亮物体(暗背景)和暗物体(亮背景)
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 必须保证核是奇数
    if blur_size > 0:
        if blur_size % 2 == 0:
            blur_size += 1
        gray = cv2.GaussianBlur(gray, (blur_size, blur_size), 0)
        
    # 提取亮目标
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # 提取暗目标
    _, thresh_inv = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    boxes = []
    for t in [thresh, thresh_inv]:
        contours, _ = cv2.findContours(t, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            boxes.append((x, y, w, h))
            
    return boxes