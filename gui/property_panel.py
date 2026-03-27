from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QComboBox, QFrame
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPalette

class PropertyPanel(QWidget):
    # 当类别被修改时发出信号，参数为新的类别索引
    class_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.classes = []
        self.colors = []
        self.current_annotation_index = -1

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        form_layout = QFormLayout()

        # 类别下拉框
        self.combo_class = QComboBox()
        self.combo_class.currentIndexChanged.connect(self.on_combo_changed)
        form_layout.addRow("类别:", self.combo_class)

        # 宽度
        self.label_width = QLabel("-")
        form_layout.addRow("宽度(w):", self.label_width)

        # 高度
        self.label_height = QLabel("-")
        form_layout.addRow("高度(h):", self.label_height)

        # 颜色显示块
        self.color_frame = QFrame()
        self.color_frame.setFixedSize(20, 20)
        self.color_frame.setAutoFillBackground(True)
        # 初始化为透明
        self.set_color_frame_bg(QColor(0, 0, 0, 0))
        form_layout.addRow("颜色:", self.color_frame)

        layout.addLayout(form_layout)
        
        self.setEnabled(False) # 默认禁用，直到选中目标

    def set_color_frame_bg(self, color):
        palette = self.color_frame.palette()
        palette.setColor(QPalette.Window, color)
        self.color_frame.setPalette(palette)

    def update_classes(self, classes, colors):
        self.classes = classes
        self.colors = colors
        
        # 刷新下拉框
        self.combo_class.blockSignals(True)
        self.combo_class.clear()
        self.combo_class.addItems(self.classes)
        self.combo_class.blockSignals(False)

    def update_info(self, annotation, img_width, img_height, index):
        self.current_annotation_index = index
        if not annotation or index == -1:
            self.setEnabled(False)
            self.label_width.setText("-")
            self.label_height.setText("-")
            self.set_color_frame_bg(QColor(0, 0, 0, 0))
            self.combo_class.blockSignals(True)
            self.combo_class.setCurrentIndex(-1)
            self.combo_class.blockSignals(False)
            return

        self.setEnabled(True)
        
        # 更新长宽 (计算实际像素或保留归一化比例，这里显示实际像素更直观)
        pixel_w = int(annotation.width * img_width)
        pixel_h = int(annotation.height * img_height)
        self.label_width.setText(f"{pixel_w} px")
        self.label_height.setText(f"{pixel_h} px")

        # 更新类别
        self.combo_class.blockSignals(True)
        if 0 <= annotation.class_id < len(self.classes):
            self.combo_class.setCurrentIndex(annotation.class_id)
            
            # 更新颜色
            color_tuple = self.colors[annotation.class_id]
            self.set_color_frame_bg(QColor(*color_tuple))
        else:
            self.combo_class.setCurrentIndex(-1)
            self.set_color_frame_bg(QColor(0, 0, 0, 0))
        self.combo_class.blockSignals(False)

    def on_combo_changed(self, idx):
        if idx >= 0 and self.current_annotation_index != -1:
            # 立即更新颜色预览
            if idx < len(self.colors):
                self.set_color_frame_bg(QColor(*self.colors[idx]))
            self.class_changed.emit(idx)
