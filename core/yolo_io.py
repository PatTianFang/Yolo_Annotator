"""
YOLO格式读写
"""
import os
from .annotation import AnnotationItem

def load_classes(filepath):
    """从 classes.txt 加载类别列表"""
    classes = []
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            classes = [line.strip() for line in f if line.strip()]
    return classes

def save_classes(filepath, classes):
    """保存类别列表到 classes.txt"""
    with open(filepath, 'w', encoding='utf-8') as f:
        for cls in classes:
            f.write(f"{cls}\n")

def load_yolo_annotations(filepath):
    """加载 YOLO 格式的 txt 标注文件"""
    annotations = []
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 5:
                    class_id = int(parts[0])
                    x_c, y_c, w, h = map(float, parts[1:])
                    annotations.append(AnnotationItem(class_id, x_c, y_c, w, h))
    return annotations

def save_yolo_annotations(filepath, annotations):
    """保存 YOLO 格式标注"""
    if not annotations:
        # 如果没有标注且文件存在，可选删除或写入空文件，这里选择写入空文件
        if os.path.exists(filepath):
            os.remove(filepath)
        return

    # 确保目录存在
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        for ann in annotations:
            f.write(ann.to_yolo_string() + "\n")
