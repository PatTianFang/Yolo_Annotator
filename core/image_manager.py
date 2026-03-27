"""
图片管理
"""
import os
import cv2
import numpy as np

class ImageManager:
    def __init__(self):
        self.image_paths = []
        self.current_index = -1
        self.current_image = None
        
    def load_directory(self, dir_path, supported_formats):
        """加载目录中的所有支持图片"""
        self.image_paths = []
        for file in os.listdir(dir_path):
            ext = os.path.splitext(file)[1].lower()
            if ext in [fmt.lower() for fmt in supported_formats]:
                self.image_paths.append(os.path.join(dir_path, file))
        self.image_paths.sort()
        self.current_index = 0 if self.image_paths else -1
        return len(self.image_paths)

    def load_image(self, path=None):
        """加载图片"""
        if path:
            if path in self.image_paths:
                self.current_index = self.image_paths.index(path)
            else:
                self.image_paths.append(path)
                self.current_index = len(self.image_paths) - 1
                
        if 0 <= self.current_index < len(self.image_paths):
            current_path = self.image_paths[self.current_index]
            # 用 cv2 支持中文路径读取
            self.current_image = cv2.imdecode(np.fromfile(current_path, dtype=np.uint8), cv2.IMREAD_COLOR)
            return True
        return False

    def next_image(self):
        """下一张"""
        if self.image_paths and self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            return self.load_image()
        return False

    def prev_image(self):
        """上一张"""
        if self.image_paths and self.current_index > 0:
            self.current_index -= 1
            return self.load_image()
        return False

    def get_current_image_path(self):
        if 0 <= self.current_index < len(self.image_paths):
            return self.image_paths[self.current_index]
        return None

    def get_current_label_path(self):
        """获取当前图片对应的 txt 文件路径"""
        img_path = self.get_current_image_path()
        if img_path:
            base_name = os.path.splitext(img_path)[0]
            return f"{base_name}.txt"
        return None
