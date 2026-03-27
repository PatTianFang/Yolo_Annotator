from PySide6.QtWidgets import QWidget, QMenu
from PySide6.QtGui import QPainter, QImage, QColor, QPen, QCursor, QFont
from PySide6.QtCore import Qt, QRect, QPoint, Signal

from core.annotation import AnnotationItem
from config import COLOR_BBOX_NORMAL, COLOR_BBOX_SELECTED, COLOR_CROSSHAIR, COLOR_BBOX_HOVER

class Canvas(QWidget):
    # 信号定义
    new_shape_created = Signal(list)  # (xmin, ymin, xmax, ymax)
    selection_changed = Signal(int)   # 选中索引
    shape_modified = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None
        self.annotations = []
        self.classes = []
        self.colors = []
        
        # 视口变换参数
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
        # 状态机
        self.mode = "EDIT"  # CREATE, EDIT
        self.selected_index = -1
        self.hovered_index = -1
        
        # 绘制相关
        self.crosshair_pos = QPoint()
        self.start_point = QPoint()
        self.current_point = QPoint()
        self.drawing = False
        self.panning = False
        self.pan_start = QPoint()
        
        # 拖拽相关
        self.dragging_shape = False
        self.drag_start_pos = QPoint()
        self.drag_start_ann = None
        self.resizing_shape = False
        self.resize_anchor = None # TL, TR, BL, BR
        
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

    def load_image(self, img_path):
        self.image = QImage(img_path)
        self.fit_window()

    def set_annotations(self, annotations):
        self.annotations = annotations
        self.selected_index = -1
        self.update()

    def set_classes_colors(self, classes, colors):
        self.classes = classes
        self.colors = colors

    def fit_window(self):
        if self.image and not self.image.isNull():
            w_ratio = self.width() / self.image.width()
            h_ratio = self.height() / self.image.height()
            self.scale = min(w_ratio, h_ratio) * 0.95
            
            # 居中
            scaled_w = self.image.width() * self.scale
            scaled_h = self.image.height() * self.scale
            self.offset_x = (self.width() - scaled_w) / 2
            self.offset_y = (self.height() - scaled_h) / 2
            self.update()

    def zoom(self, factor, center=None):
        if not self.image: return
        old_scale = self.scale
        self.scale *= factor
        self.scale = max(0.01, min(self.scale, 50.0))
        
        # 以鼠标为中心缩放
        if center:
            delta_scale = self.scale / old_scale
            self.offset_x = center.x() - (center.x() - self.offset_x) * delta_scale
            self.offset_y = center.y() - (center.y() - self.offset_y) * delta_scale
            
        self.update()

    def paintEvent(self, event):
        if not self.image or self.image.isNull():
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 应用变换
        painter.translate(self.offset_x, self.offset_y)
        painter.scale(self.scale, self.scale)
        
        # 绘制图片
        painter.drawImage(0, 0, self.image)
        
        # 绘制标注框
        img_w = self.image.width()
        img_h = self.image.height()
        
        for i, ann in enumerate(self.annotations):
            xmin, ymin, xmax, ymax = ann.get_pixel_rect(img_w, img_h)
            rect = QRect(xmin, ymin, xmax - xmin, ymax - ymin)
            
            # 获取颜色
            color_rgb = COLOR_BBOX_NORMAL
            if self.colors and ann.class_id < len(self.colors):
                color_rgb = self.colors[ann.class_id]
                
            color = QColor(*color_rgb)
            
            if i == self.selected_index:
                color = QColor(*COLOR_BBOX_SELECTED)
                pen_width = 3 / self.scale
            elif i == self.hovered_index:
                color = QColor(*COLOR_BBOX_HOVER)
                pen_width = 2 / self.scale
            else:
                pen_width = 2 / self.scale
                
            painter.setPen(QPen(color, pen_width, Qt.SolidLine))
            painter.drawRect(rect)
            
            # 绘制标签背景和文字
            if ann.class_id < len(self.classes):
                label_name = self.classes[ann.class_id]
                font = QFont("Arial", max(int(12 / self.scale), 1))
                painter.setFont(font)
                fm = painter.fontMetrics()
                text_rect = fm.boundingRect(label_name)
                
                # 绘制半透明背景
                bg_rect = QRect(xmin, ymin - text_rect.height() - 2, text_rect.width() + 4, text_rect.height() + 2)
                painter.fillRect(bg_rect, QColor(color.red(), color.green(), color.blue(), 150))
                
                painter.setPen(QPen(Qt.white))
                painter.drawText(xmin + 2, ymin - 2, label_name)

        # 绘制正在创建的框
        if self.mode == "CREATE" and self.drawing:
            xmin = min(self.start_point.x(), self.current_point.x())
            ymin = min(self.start_point.y(), self.current_point.y())
            w = abs(self.start_point.x() - self.current_point.x())
            h = abs(self.start_point.y() - self.current_point.y())
            
            painter.setPen(QPen(QColor(0, 0, 0), 2 / self.scale, Qt.DashLine))
            painter.drawRect(xmin, ymin, w, h)

        # 取消变换绘制十字准星（基于屏幕坐标）
        painter.resetTransform()
        if self.crosshair_pos.x() > 0 and self.crosshair_pos.y() > 0:
            painter.setPen(QPen(QColor(*COLOR_CROSSHAIR), 1, Qt.DotLine))
            painter.drawLine(0, self.crosshair_pos.y(), self.width(), self.crosshair_pos.y())
            painter.drawLine(self.crosshair_pos.x(), 0, self.crosshair_pos.x(), self.height())

    def screen_to_image(self, point):
        """屏幕坐标转图片坐标"""
        x = (point.x() - self.offset_x) / self.scale
        y = (point.y() - self.offset_y) / self.scale
        return QPoint(int(x), int(y))

    def get_shape_at(self, img_pt):
        """获取点击位置的标注框索引"""
        if not self.image: return -1
        img_w, img_h = self.image.width(), self.image.height()
        
        # 逆序遍历，使上层覆盖优先被选中
        for i in range(len(self.annotations) - 1, -1, -1):
            ann = self.annotations[i]
            xmin, ymin, xmax, ymax = ann.get_pixel_rect(img_w, img_h)
            
            # 添加点击容差
            tolerance = 5 / self.scale
            rect = QRect(xmin - tolerance, ymin - tolerance, 
                         xmax - xmin + 2*tolerance, ymax - ymin + 2*tolerance)
            if rect.contains(img_pt):
                return i
        return -1

    def get_resize_anchor(self, ann, img_pt):
        """检测是否在角点附近用于缩放"""
        img_w, img_h = self.image.width(), self.image.height()
        xmin, ymin, xmax, ymax = ann.get_pixel_rect(img_w, img_h)
        tolerance = 10 / self.scale
        
        corners = {
            "TL": QPoint(xmin, ymin),
            "TR": QPoint(xmax, ymin),
            "BL": QPoint(xmin, ymax),
            "BR": QPoint(xmax, ymax)
        }
        
        for anchor, pt in corners.items():
            if (abs(pt.x() - img_pt.x()) < tolerance and 
                abs(pt.y() - img_pt.y()) < tolerance):
                return anchor
        return None

    def mousePressEvent(self, event):
        if not self.image: return
        self.setFocus()
        img_pt = self.screen_to_image(event.pos())
        
        if event.button() == Qt.LeftButton:
            if self.mode == "CREATE":
                self.drawing = True
                self.start_point = img_pt
                self.current_point = img_pt
            elif self.mode == "EDIT":
                idx = self.get_shape_at(img_pt)
                if idx != -1:
                    self.selected_index = idx
                    self.selection_changed.emit(idx)
                    
                    # 检查是否点击角点进行缩放
                    ann = self.annotations[idx]
                    anchor = self.get_resize_anchor(ann, img_pt)
                    if anchor:
                        self.resizing_shape = True
                        self.resize_anchor = anchor
                    else:
                        self.dragging_shape = True
                    
                    self.drag_start_pos = img_pt
                    self.drag_start_ann = ann.clone()
                else:
                    self.selected_index = -1
                    self.selection_changed.emit(-1)
                    
        elif event.button() == Qt.RightButton:
            self.panning = True
            self.pan_start = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            
        self.update()

    def mouseMoveEvent(self, event):
        if not self.image: return
        self.crosshair_pos = event.pos()
        img_pt = self.screen_to_image(event.pos())
        
        if self.mode == "CREATE" and self.drawing:
            self.current_point = img_pt
            
        elif self.mode == "EDIT":
            if self.dragging_shape and self.selected_index != -1:
                # 移动框
                dx = img_pt.x() - self.drag_start_pos.x()
                dy = img_pt.y() - self.drag_start_pos.y()
                
                img_w, img_h = self.image.width(), self.image.height()
                norm_dx = dx / img_w
                norm_dy = dy / img_h
                
                ann = self.annotations[self.selected_index]
                ann.x_center = self.drag_start_ann.x_center + norm_dx
                ann.y_center = self.drag_start_ann.y_center + norm_dy
                
            elif self.resizing_shape and self.selected_index != -1:
                # 缩放框
                dx = img_pt.x() - self.drag_start_pos.x()
                dy = img_pt.y() - self.drag_start_pos.y()
                
                img_w, img_h = self.image.width(), self.image.height()
                norm_dx = dx / img_w
                norm_dy = dy / img_h
                
                ann = self.annotations[self.selected_index]
                
                if self.resize_anchor == "BR":
                    ann.width = self.drag_start_ann.width + norm_dx
                    ann.height = self.drag_start_ann.height + norm_dy
                    ann.x_center = self.drag_start_ann.x_center + norm_dx / 2
                    ann.y_center = self.drag_start_ann.y_center + norm_dy / 2
                # 其他角点的逻辑可以类似补充，暂简化只实现右下角或统一处理
            else:
                # Hover detection
                old_hover = self.hovered_index
                self.hovered_index = self.get_shape_at(img_pt)
                
                # 更新鼠标样式
                if self.hovered_index != -1:
                    anchor = self.get_resize_anchor(self.annotations[self.hovered_index], img_pt)
                    if anchor in ["TL", "BR"]:
                        self.setCursor(Qt.SizeFDiagCursor)
                    elif anchor in ["TR", "BL"]:
                        self.setCursor(Qt.SizeBDiagCursor)
                    else:
                        self.setCursor(Qt.SizeAllCursor)
                else:
                    self.setCursor(Qt.CrossCursor)

        if self.panning:
            delta = event.pos() - self.pan_start
            self.offset_x += delta.x()
            self.offset_y += delta.y()
            self.pan_start = event.pos()
            
        self.update()

    def mouseReleaseEvent(self, event):
        if not self.image: return
        img_pt = self.screen_to_image(event.pos())
        
        if event.button() == Qt.LeftButton:
            if self.mode == "CREATE" and self.drawing:
                self.drawing = False
                self.current_point = img_pt
                
                xmin = min(self.start_point.x(), self.current_point.x())
                ymin = min(self.start_point.y(), self.current_point.y())
                xmax = max(self.start_point.x(), self.current_point.x())
                ymax = max(self.start_point.y(), self.current_point.y())
                
                if xmax - xmin > 5 and ymax - ymin > 5:
                    self.new_shape_created.emit([xmin, ymin, xmax, ymax])
                    
            elif self.mode == "EDIT":
                if self.dragging_shape or self.resizing_shape:
                    self.dragging_shape = False
                    self.resizing_shape = False
                    self.shape_modified.emit()
                    
        elif event.button() == Qt.RightButton:
            self.panning = False
            self.setCursor(Qt.CrossCursor)
            
        self.update()

    def wheelEvent(self, event):
        if not self.image: return
        factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        self.zoom(factor, event.position().toPoint())
