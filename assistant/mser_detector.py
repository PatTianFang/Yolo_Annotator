import cv2

def detect_mser(image, delta=5):
    """
    基于 MSER (Maximally Stable Extremal Regions) 的斑点/文本区域提取
    """
    mser = cv2.MSER_create(delta=delta)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    regions, _ = mser.detectRegions(gray)
    
    boxes = []
    for p in regions:
        x, y, w, h = cv2.boundingRect(p)
        boxes.append((x, y, w, h))
        
    return boxes