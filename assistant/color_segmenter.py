import cv2
import numpy as np
from sklearn.cluster import KMeans

def segment_color(image, k=3):
    """
    基于 K-Means 颜色聚类分割
    返回每个聚类块的 bounding boxes: (x, y, w, h)
    """
    # 将图像转换为一维数组
    pixel_values = image.reshape((-1, 3))
    pixel_values = np.float32(pixel_values)
    
    # OpenCV K-Means
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, _ = cv2.kmeans(pixel_values, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    
    labels = labels.flatten()
    segmented_image = labels.reshape(image.shape[:2])
    
    boxes = []
    # 遍历每个聚类类别
    for i in range(k):
        mask = np.uint8(segmented_image == i) * 255
        # 开运算去除噪点
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            boxes.append((x, y, w, h))
            
    return boxes
