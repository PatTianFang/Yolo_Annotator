import cv2
import numpy as np
import os

# 设置Ultralytics配置目录为当前目录，避免权限问题
os.environ['YOLO_CONFIG_DIR'] = os.path.dirname(os.path.abspath(__file__))

from ultralytics import YOLO


# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 默认模型文件夹路径
DEFAULT_MODEL_DIR = os.path.join(PROJECT_ROOT, "model")

def detect_yolo(image, model_path=None, conf_threshold=0.4, **kwargs):
    """
    使用YOLO模型检测目标并返回边界框
    
    Args:
        image: 输入图像
        model_path: YOLO模型权重文件路径，默认为None（自动查找model文件夹中的第一个.pt文件）
        conf_threshold: 置信度阈值
        **kwargs: 其他参数
    
    Returns:
        list: 检测到的边界框列表，格式为 [(x, y, w, h), ...]
    """
    try:
        # 如果未指定模型路径，自动查找model文件夹中的.pt文件
        if model_path is None or model_path == '':
            if os.path.exists(DEFAULT_MODEL_DIR):
                pt_files = [f for f in os.listdir(DEFAULT_MODEL_DIR) if f.endswith('.pt')]
                if pt_files:
                    model_path = os.path.join(DEFAULT_MODEL_DIR, pt_files[0])
                    print(f"自动使用模型: {model_path}")
                else:
                    print(f"错误: model文件夹中没有找到.pt模型文件")
                    return []
            else:
                print(f"错误: model文件夹不存在: {DEFAULT_MODEL_DIR}")
                return []
        
        # 加载YOLO模型
        model = YOLO(model_path)
        
        # 执行检测
        results = model(image, conf=conf_threshold)
        
        # 提取边界框
        boxes = []
        for result in results:
            for box in result.boxes:
                # 获取边界框坐标 (x1, y1, x2, y2)
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                # 获取类别ID和置信度
                class_id = int(box.cls[0].item())
                conf = box.conf[0].item()
                # 转换为 (x, y, w, h, class_id, conf) 格式
                x = int(x1)
                y = int(y1)
                w = int(x2 - x1)
                h = int(y2 - y1)
                boxes.append((x, y, w, h, class_id, conf))
        
        return boxes
    except Exception as e:
        print(f"YOLO检测错误: {e}")
        return []
