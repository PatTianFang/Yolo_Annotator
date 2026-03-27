from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, \
    QDockWidget, QListWidget, QToolBar, QStatusBar, QFileDialog, QMessageBox, QComboBox, QDialog
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtCore import Qt

from core.image_manager import ImageManager
from core.history import HistoryManager
from core.yolo_io import load_yolo_annotations, save_yolo_annotations, load_classes, save_classes
from core.annotation import AnnotationItem
from utils.helpers import generate_colors

from gui.canvas import Canvas
from gui.class_manager import ClassManager
from gui.label_dialog import LabelDialog
from gui.property_panel import PropertyPanel
from gui.assistant_panel import AssistantPanel
from gui.config_dialog import ConfigDialog
from gui.load_config_dialog import LoadConfigDialog

import os
import cv2
import numpy as np
import yaml
from assistant.box_proposer import propose_boxes

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YOLO 辅助标注软件")
        self.resize(1200, 800)
        
        # 设置窗口图标
        self.set_window_icon()

        # 核心管理器
        self.image_manager = ImageManager()
        self.history_manager = HistoryManager()
        
        self.classes = []
        self.colors = []
        self.annotations = []
        
        # UI 初始化
        self.init_ui()
        self.update_ui_state()

    def set_window_icon(self):
        """设置窗口图标"""
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "logo.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
    
    def init_ui(self):
        # 中心画布
        self.canvas = Canvas(self)
        self.setCentralWidget(self.canvas)
        self.canvas.new_shape_created.connect(self.on_new_shape)
        self.canvas.selection_changed.connect(self.on_selection_changed)
        self.canvas.shape_modified.connect(self.on_shape_modified)

        # 停靠窗口 - 文件列表
        self.file_dock = QDockWidget("文件列表", self)
        self.file_list = QListWidget()
        self.file_list.currentRowChanged.connect(self.on_file_selected)
        self.file_dock.setWidget(self.file_list)
        self.addDockWidget(Qt.RightDockWidgetArea, self.file_dock)

        # 停靠窗口 - 类别列表
        self.class_dock = QDockWidget("类别管理", self)
        self.class_manager = ClassManager()
        self.class_manager.class_changed.connect(self.on_class_changed)
        self.class_dock.setWidget(self.class_manager)
        self.addDockWidget(Qt.RightDockWidgetArea, self.class_dock)

        # 停靠窗口 - 属性管理
        self.property_dock = QDockWidget("属性管理", self)
        self.property_panel = PropertyPanel()
        self.property_panel.class_changed.connect(self.on_property_class_changed)
        self.property_dock.setWidget(self.property_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, self.property_dock)
        
        # 停靠窗口 - 辅助标注设置
        self.assistant_dock = QDockWidget("辅助标注面板", self)
        self.assistant_panel = AssistantPanel()
        self.assistant_panel.run_requested.connect(self.run_assistant_with_params)
        self.assistant_dock.setWidget(self.assistant_panel)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.assistant_dock)

        # 创建动作与工具栏
        self.create_actions()
        self.create_toolbar()
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def create_actions(self):
        self.act_open_dir = QAction("打开目录", self)
        self.act_open_dir.triggered.connect(self.open_dir)
        
        self.act_save = QAction("保存 (Ctrl+S)", self)
        self.act_save.setShortcut("Ctrl+S")
        self.act_save.triggered.connect(self.save_annotations)
        
        self.act_prev = QAction("上一张 (A)", self)
        self.act_prev.setShortcut("A")
        self.act_prev.triggered.connect(self.prev_image)
        
        self.act_next = QAction("下一张 (D)", self)
        self.act_next.setShortcut("D")
        self.act_next.triggered.connect(self.next_image)
        
        self.act_create = QAction("创建框 (W)", self)
        self.act_create.setShortcut("W")
        self.act_create.setCheckable(True)
        self.act_create.triggered.connect(self.toggle_create_mode)
        
        self.act_delete = QAction("删除选框 (Del)", self)
        self.act_delete.setShortcut("Del")
        self.act_delete.triggered.connect(self.delete_selected_shape)
        
        self.act_undo = QAction("撤销 (Ctrl+Z)", self)
        self.act_undo.setShortcut("Ctrl+Z")
        self.act_undo.triggered.connect(self.undo)
        
        self.act_redo = QAction("重做 (Ctrl+Shift+Z)", self)
        self.act_redo.setShortcut("Ctrl+Shift+Z")
        self.act_redo.triggered.connect(self.redo)
        
        # 配置相关动作
        self.act_save_config = QAction("添加配置", self)
        self.act_save_config.triggered.connect(self.open_save_config_dialog)
        
        self.act_load_config = QAction("加载配置", self)
        self.act_load_config.triggered.connect(self.open_load_config_dialog)

    def create_toolbar(self):
        toolbar = QToolBar("主工具栏")
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        
        toolbar.addAction(self.act_open_dir)
        toolbar.addAction(self.act_save)
        toolbar.addSeparator()
        toolbar.addAction(self.act_prev)
        toolbar.addAction(self.act_next)
        toolbar.addSeparator()
        toolbar.addAction(self.act_create)
        toolbar.addAction(self.act_delete)
        toolbar.addSeparator()
        toolbar.addAction(self.act_undo)
        toolbar.addAction(self.act_redo)
        toolbar.addSeparator()
        toolbar.addAction(self.act_save_config)
        toolbar.addAction(self.act_load_config)
        
    def open_save_config_dialog(self):
        """打开保存配置对话框"""
        dialog = ConfigDialog(self)
        dialog.exec()

    def open_load_config_dialog(self):
        """打开加载配置对话框"""
        dialog = LoadConfigDialog(self)
        if dialog.exec() == QDialog.Accepted:
            config_data = dialog.get_loaded_config()
            if config_data:
                self.apply_config_to_ui(config_data)
    
    def apply_config_to_ui(self, config_data):
        """将加载的配置应用到UI"""
        try:
            # 更新辅助面板中的参数值
            panel = self.assistant_panel
            
            # 边缘检测参数
            if "EDGE_CANNY_THRESHOLD1" in config_data:
                panel.spin_canny_t1.setValue(config_data["EDGE_CANNY_THRESHOLD1"])
            if "EDGE_CANNY_THRESHOLD2" in config_data:
                panel.spin_canny_t2.setValue(config_data["EDGE_CANNY_THRESHOLD2"])
            
            # 颜色分割参数
            if "COLOR_KMEANS_K" in config_data:
                panel.spin_kmeans_k.setValue(config_data["COLOR_KMEANS_K"])
            
            # MSER参数
            if "MSER_DELTA" in config_data:
                panel.spin_mser_delta.setValue(config_data["MSER_DELTA"])
            
            # OTSU参数
            if "OTSU_BLUR_SIZE" in config_data:
                panel.spin_otsu_blur.setValue(config_data["OTSU_BLUR_SIZE"])
            
            # GrabCut参数
            if "GRABCUT_ITER_COUNT" in config_data:
                panel.spin_grabcut_iter.setValue(config_data["GRABCUT_ITER_COUNT"])
            if "GRABCUT_MARGIN" in config_data:
                panel.spin_grabcut_margin.setValue(config_data["GRABCUT_MARGIN"])
            
            # 通用参数
            if "BOX_MIN_AREA" in config_data:
                panel.spin_min_area.setValue(config_data["BOX_MIN_AREA"])
            if "BOX_NMS_THRESHOLD" in config_data:
                panel.double_nms.setValue(config_data["BOX_NMS_THRESHOLD"])
            
            QMessageBox.information(self, "成功", "配置已加载并应用到界面！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"应用配置失败:\n{str(e)}")
        
    def open_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择图片目录")
        if dir_path:
            # 尝试加载 classes.txt
            classes_path = os.path.join(dir_path, "classes.txt")
            if os.path.exists(classes_path):
                self.classes = load_classes(classes_path)
            else:
                self.classes = []
            
            self.colors = generate_colors(max(len(self.classes), 10))
            self.class_manager.load_classes(self.classes, self.colors)
            self.canvas.set_classes_colors(self.classes, self.colors)
            
            count = self.image_manager.load_directory(dir_path, [".jpg", ".png", ".bmp", ".jpeg"])
            if count > 0:
                self.file_list.clear()
                for p in self.image_manager.image_paths:
                    self.file_list.addItem(os.path.basename(p))
                
                self.load_current_image()
            else:
                QMessageBox.warning(self, "警告", "未找到支持的图片文件！")

    def load_current_image(self):
        if self.image_manager.load_image():
            img_path = self.image_manager.get_current_image_path()
            self.canvas.load_image(img_path)
            
            # 同步文件列表选中
            self.file_list.setCurrentRow(self.image_manager.current_index)
            
            # 加载标注
            label_path = self.image_manager.get_current_label_path()
            if os.path.exists(label_path):
                self.annotations = load_yolo_annotations(label_path)
            else:
                self.annotations = []
                
            self.canvas.set_annotations(self.annotations)
            self.history_manager.clear()
            self.save_history()
            
            self.update_ui_state()
            
            # 状态栏
            img = self.image_manager.current_image
            if img is not None:
                h, w = img.shape[:2]
                self.status_bar.showMessage(f"{os.path.basename(img_path)} - {w}x{h}")

    def on_file_selected(self, index):
        if index != self.image_manager.current_index and index >= 0:
            # TODO: 自动保存开关
            self.save_annotations()
            self.image_manager.current_index = index
            self.load_current_image()

    def prev_image(self):
        self.save_annotations()
        if self.image_manager.prev_image():
            self.load_current_image()

    def next_image(self):
        self.save_annotations()
        if self.image_manager.next_image():
            self.load_current_image()

    def toggle_create_mode(self):
        if self.act_create.isChecked():
            self.canvas.mode = "CREATE"
            self.canvas.selected_index = -1
        else:
            self.canvas.mode = "EDIT"
        self.canvas.update()

    def on_new_shape(self, coords):
        xmin, ymin, xmax, ymax = coords
        
        # 弹出选择标签对话框
        dialog = LabelDialog(self.classes, self)
        if dialog.exec():
            label_name = dialog.get_class()
            if label_name not in self.classes:
                self.classes.append(label_name)
                self.colors = generate_colors(max(len(self.classes), 10))
                self.class_manager.load_classes(self.classes, self.colors)
                self.canvas.set_classes_colors(self.classes, self.colors)
                # 保存 classes.txt
                dir_path = os.path.dirname(self.image_manager.get_current_image_path())
                save_classes(os.path.join(dir_path, "classes.txt"), self.classes)
                
            class_id = self.classes.index(label_name)
            
            img_w = self.canvas.image.width()
            img_h = self.canvas.image.height()
            
            ann = AnnotationItem.from_pixel_rect(class_id, xmin, ymin, xmax, ymax, img_w, img_h)
            self.annotations.append(ann)
            
            self.canvas.mode = "EDIT"
            self.act_create.setChecked(False)
            self.canvas.selected_index = len(self.annotations) - 1
            self.canvas.update()
            
            self.save_history()

    def on_selection_changed(self, index):
        if self.image_manager.current_image is not None and index != -1 and index < len(self.annotations):
            img_h, img_w = self.image_manager.current_image.shape[:2]
            self.property_panel.update_classes(self.classes, self.colors)
            self.property_panel.update_info(self.annotations[index], img_w, img_h, index)
        else:
            self.property_panel.update_info(None, 0, 0, -1)

    def on_property_class_changed(self, class_idx):
        idx = self.canvas.selected_index
        if idx != -1 and idx < len(self.annotations):
            self.annotations[idx].class_id = class_idx
            self.canvas.update()
            self.save_history()

    def on_shape_modified(self):
        self.save_history()
        # 更新属性面板的长宽
        self.on_selection_changed(self.canvas.selected_index)

    def delete_selected_shape(self):
        idx = self.canvas.selected_index
        if idx != -1:
            del self.annotations[idx]
            self.canvas.selected_index = -1
            self.canvas.update()
            self.save_history()

    def save_annotations(self):
        label_path = self.image_manager.get_current_label_path()
        if label_path:
            save_yolo_annotations(label_path, self.annotations)

    def on_class_changed(self):
        self.canvas.update()
        dir_path = os.path.dirname(self.image_manager.get_current_image_path())
        if dir_path:
            save_classes(os.path.join(dir_path, "classes.txt"), self.classes)

    def save_history(self):
        # 将当前的 annotations 的副本存入历史
        state = [ann.clone() for ann in self.annotations]
        self.history_manager.push(state)
        self.update_ui_state()

    def undo(self):
        state = self.history_manager.undo()
        if state is not None:
            self.annotations = [ann.clone() for ann in state]
            self.canvas.set_annotations(self.annotations)
            self.update_ui_state()

    def redo(self):
        state = self.history_manager.redo()
        if state is not None:
            self.annotations = [ann.clone() for ann in state]
            self.canvas.set_annotations(self.annotations)
            self.update_ui_state()

    def update_ui_state(self):
        self.act_undo.setEnabled(self.history_manager.can_undo())
        self.act_redo.setEnabled(self.history_manager.can_redo())

    def run_assistant_with_params(self, mode, params):
        if self.image_manager.current_image is None:
            return
            
        image = self.image_manager.current_image
        new_anns = propose_boxes(image, mode=mode, **params)
        
        if new_anns:
            if not self.classes:
                self.classes.append("auto_gen")
                self.colors = generate_colors(max(len(self.classes), 10))
                self.class_manager.load_classes(self.classes, self.colors)
                self.canvas.set_classes_colors(self.classes, self.colors)
                
            for ann in new_anns:
                ann.class_id = 0
                self.annotations.append(ann)
                
            self.canvas.update()
            self.save_history()
            QMessageBox.information(self, "辅助标注", f"成功生成 {len(new_anns)} 个候选框！")
        else:
            QMessageBox.information(self, "辅助标注", "未检测到有效物体。")

    def run_assistant(self):
        if self.image_manager.current_image is None:
            return
            
        mode_text = self.assistant_combo.currentText()
        if mode_text == "边缘检测":
            mode = "edge"
        elif mode_text == "颜色分割":
            mode = "color"
        elif mode_text == "显著性检测":
            mode = "saliency"
        else:
            return

        image = self.image_manager.current_image
        new_anns = propose_boxes(image, mode=mode, min_area=400, nms_threshold=0.3)
        
        if new_anns:
            # 这里简单起见将生成框标签设为 0（需要确保 classes 有元素）
            if not self.classes:
                self.classes.append("auto_gen")
                self.colors = generate_colors(max(len(self.classes), 10))
                self.class_manager.load_classes(self.classes, self.colors)
                self.canvas.set_classes_colors(self.classes, self.colors)
                
            for ann in new_anns:
                ann.class_id = 0
                self.annotations.append(ann)
                
            self.canvas.update()
            self.save_history()
            QMessageBox.information(self, "辅助标注", f"成功生成 {len(new_anns)} 个候选框！")
        else:
            QMessageBox.information(self, "辅助标注", "未检测到有效物体。")

    def keyPressEvent(self, event):
        # 快捷键支持数字切换标签类别（如果选中了某个框）
        key = event.key()
        if Qt.Key_1 <= key <= Qt.Key_9:
            class_idx = key - Qt.Key_1
            if class_idx < len(self.classes) and self.canvas.selected_index != -1:
                self.annotations[self.canvas.selected_index].class_id = class_idx
                self.canvas.update()
                self.save_history()
        super().keyPressEvent(event)
