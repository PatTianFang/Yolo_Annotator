import cv2
import numpy as np

def detect_saliency(image):
    """
    基于显著性检测（简单实现，使用 OpenCV 的 Saliency API 若存在，否则使用简单的二值化近似）
    """
    # 使用谱残差法或直接提供一个通用的 fallback
    # OpenCV contrib 中才有 cv2.saliency
    try:
        saliency = cv2.saliency.StaticSaliencySpectralResidual_create()
        (success, saliencyMap) = saliency.computeSaliency(image)
        saliencyMap = (saliencyMap * 255).astype("uint8")
        _, thresh = cv2.threshold(saliencyMap, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    except AttributeError:
        # Fallback 策略: 高亮部分检测
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (11, 11), 0)
        _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)
    
    # 提取轮廓
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        boxes.append((x, y, w, h))
        
    return boxes
