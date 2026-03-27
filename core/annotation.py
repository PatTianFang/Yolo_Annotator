"""
标注数据模型
"""

class AnnotationItem:
    def __init__(self, class_id, x_center, y_center, width, height):
        """
        初始化一个 YOLO 格式的标注项
        所有坐标均为 0-1 的归一化值
        """
        self.class_id = class_id
        self.x_center = float(x_center)
        self.y_center = float(y_center)
        self.width = float(width)
        self.height = float(height)

    def to_yolo_string(self):
        """转为 YOLO 格式字符串"""
        return f"{self.class_id} {self.x_center:.6f} {self.y_center:.6f} {self.width:.6f} {self.height:.6f}"
    
    def get_pixel_rect(self, img_width, img_height):
        """获取绝对像素坐标 (xmin, ymin, xmax, ymax)"""
        x_c = self.x_center * img_width
        y_c = self.y_center * img_height
        w = self.width * img_width
        h = self.height * img_height
        
        xmin = x_c - w / 2
        ymin = y_c - h / 2
        xmax = x_c + w / 2
        ymax = y_c + h / 2
        return int(xmin), int(ymin), int(xmax), int(ymax)

    def clone(self):
        """克隆当前标注项"""
        return AnnotationItem(self.class_id, self.x_center, self.y_center, self.width, self.height)

    @classmethod
    def from_pixel_rect(cls, class_id, xmin, ymin, xmax, ymax, img_width, img_height):
        """从像素矩形创建归一化标注"""
        # 防止越界
        xmin = max(0, min(xmin, img_width))
        xmax = max(0, min(xmax, img_width))
        ymin = max(0, min(ymin, img_height))
        ymax = max(0, min(ymax, img_height))
        
        w = (xmax - xmin) / img_width
        h = (ymax - ymin) / img_height
        x_c = (xmin + xmax) / 2 / img_width
        y_c = (ymin + ymax) / 2 / img_height
        return cls(class_id, x_c, y_c, w, h)
