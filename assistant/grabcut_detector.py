import cv2
import numpy as np

def detect_grabcut(image, iter_count=5, margin=10):
    """
    基于 GrabCut 算法的自动前景分割
    """
    h, w = image.shape[:2]
    
    # 确保 margin 不越界
    margin_x = min(margin, w // 4)
    margin_y = min(margin, h // 4)
    
    # 以图像边缘内缩一定像素的矩形作为初始前景范围
    rect = (margin_x, margin_y, w - 2 * margin_x, h - 2 * margin_y)
    
    mask = np.zeros((h, w), np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)
    
    boxes = []
    try:
        cv2.grabCut(image, mask, rect, bgdModel, fgdModel, iter_count, cv2.GC_INIT_WITH_RECT)
        
        # 0和2代表背景，1和3代表前景
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        
        # 开闭运算去噪和平滑
        kernel = np.ones((5, 5), np.uint8)
        mask2 = cv2.morphologyEx(mask2, cv2.MORPH_OPEN, kernel)
        mask2 = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            x, y, bw, bh = cv2.boundingRect(cnt)
            boxes.append((x, y, bw, bh))
    except Exception:
        pass
        
    return boxes