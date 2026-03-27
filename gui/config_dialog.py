from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QFormLayout, QSpinBox, QDoubleSpinBox, QPushButton,
    QFileDialog, QLineEdit, QLabel, QMessageBox
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
import config
import yaml
import os


class ConfigDialog(QDialog):
    """配置对话框 - 用于编辑和保存算法参数配置"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_file_path = None
        self.setWindowTitle("添加配置")
        self.resize(500, 600)
        
        # 设置窗口图标
        self.set_window_icon()
        
        self.init_ui()
        self.load_current_config()
    
    def set_window_icon(self):
        """设置窗口图标"""
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "logo.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 文件路径选择
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("选择配置文件路径...")
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_file)
        
        path_layout.addWidget(QLabel("配置文件:"))
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)
        
        # 编辑模式：显示参数标签页
        self.create_tabs()
        layout.addWidget(self.tabs)
        
        # 保存按钮
        save_btn = QPushButton("保存配置")
        save_btn.clicked.connect(self.save_config)
        layout.addWidget(save_btn)
    
    def create_tabs(self):
        """创建参数配置标签页"""
        self.tabs = QTabWidget()
        
        # 边缘检测参数
        self.tab_edge = self.create_edge_tab()
        self.tabs.addTab(self.tab_edge, "边缘检测")
        
        # 颜色分割参数
        self.tab_color = self.create_color_tab()
        self.tabs.addTab(self.tab_color, "颜色分割")
        
        # MSER参数
        self.tab_mser = self.create_mser_tab()
        self.tabs.addTab(self.tab_mser, "MSER")
        
        # OTSU参数
        self.tab_otsu = self.create_otsu_tab()
        self.tabs.addTab(self.tab_otsu, "OTSU")
        
        # GrabCut参数
        self.tab_grabcut = self.create_grabcut_tab()
        self.tabs.addTab(self.tab_grabcut, "GrabCut")
        
        # 通用参数
        self.tab_general = self.create_general_tab()
        self.tabs.addTab(self.tab_general, "通用参数")
    
    def create_edge_tab(self):
        """边缘检测参数标签页"""
        widget = QWidget()
        form = QFormLayout(widget)
        
        self.spin_canny_t1 = QSpinBox()
        self.spin_canny_t1.setRange(config.EDGE_CANNY_THRESHOLD_MIN, config.EDGE_CANNY_THRESHOLD_MAX)
        self.spin_canny_t1.setValue(config.EDGE_CANNY_THRESHOLD1)
        form.addRow("Canny低阈值:", self.spin_canny_t1)
        
        self.spin_canny_t2 = QSpinBox()
        self.spin_canny_t2.setRange(config.EDGE_CANNY_THRESHOLD_MIN, config.EDGE_CANNY_THRESHOLD_MAX)
        self.spin_canny_t2.setValue(config.EDGE_CANNY_THRESHOLD2)
        form.addRow("Canny高阈值:", self.spin_canny_t2)
        
        self.spin_edge_blur = QSpinBox()
        self.spin_edge_blur.setRange(1, 31)
        self.spin_edge_blur.setValue(config.EDGE_GAUSSIAN_BLUR_SIZE)
        form.addRow("高斯模糊核大小:", self.spin_edge_blur)
        
        self.spin_edge_dilate_iter = QSpinBox()
        self.spin_edge_dilate_iter.setRange(0, 10)
        self.spin_edge_dilate_iter.setValue(config.EDGE_DILATE_ITERATIONS)
        form.addRow("膨胀迭代次数:", self.spin_edge_dilate_iter)
        
        self.spin_edge_dilate_kernel = QSpinBox()
        self.spin_edge_dilate_kernel.setRange(1, 15)
        self.spin_edge_dilate_kernel.setValue(config.EDGE_DILATE_KERNEL_SIZE)
        form.addRow("膨胀核大小:", self.spin_edge_dilate_kernel)
        
        return widget
    
    def create_color_tab(self):
        """颜色分割参数标签页"""
        widget = QWidget()
        form = QFormLayout(widget)
        
        self.spin_kmeans_k = QSpinBox()
        self.spin_kmeans_k.setRange(config.COLOR_KMEANS_K_MIN, config.COLOR_KMEANS_K_MAX)
        self.spin_kmeans_k.setValue(config.COLOR_KMEANS_K)
        form.addRow("聚类数(K):", self.spin_kmeans_k)
        
        self.spin_kmeans_eps = QDoubleSpinBox()
        self.spin_kmeans_eps.setRange(0.1, 10.0)
        self.spin_kmeans_eps.setSingleStep(0.1)
        self.spin_kmeans_eps.setValue(config.COLOR_KMEANS_CRITERIA_EPS)
        form.addRow("收敛epsilon:", self.spin_kmeans_eps)
        
        self.spin_kmeans_max_iter = QSpinBox()
        self.spin_kmeans_max_iter.setRange(1, 100)
        self.spin_kmeans_max_iter.setValue(config.COLOR_KMEANS_CRITERIA_MAX_ITER)
        form.addRow("最大迭代次数:", self.spin_kmeans_max_iter)
        
        self.spin_kmeans_attempts = QSpinBox()
        self.spin_kmeans_attempts.setRange(1, 20)
        self.spin_kmeans_attempts.setValue(config.COLOR_KMEANS_ATTEMPTS)
        form.addRow("尝试次数:", self.spin_kmeans_attempts)
        
        self.spin_color_morph = QSpinBox()
        self.spin_color_morph.setRange(1, 31)
        self.spin_color_morph.setSingleStep(2)
        self.spin_color_morph.setValue(config.COLOR_MORPH_OPEN_KERNEL_SIZE)
        form.addRow("开运算核大小:", self.spin_color_morph)
        
        return widget
    
    def create_mser_tab(self):
        """MSER参数标签页"""
        widget = QWidget()
        form = QFormLayout(widget)
        
        self.spin_mser_delta = QSpinBox()
        self.spin_mser_delta.setRange(config.MSER_DELTA_MIN, config.MSER_DELTA_MAX)
        self.spin_mser_delta.setValue(config.MSER_DELTA)
        form.addRow("MSER Delta:", self.spin_mser_delta)
        
        return widget
    
    def create_otsu_tab(self):
        """OTSU参数标签页"""
        widget = QWidget()
        form = QFormLayout(widget)
        
        self.spin_otsu_blur = QSpinBox()
        self.spin_otsu_blur.setRange(config.OTSU_BLUR_SIZE_MIN, config.OTSU_BLUR_SIZE_MAX)
        self.spin_otsu_blur.setSingleStep(config.OTSU_BLUR_SIZE_STEP)
        self.spin_otsu_blur.setValue(config.OTSU_BLUR_SIZE)
        form.addRow("高斯模糊核大小:", self.spin_otsu_blur)
        
        return widget
    
    def create_grabcut_tab(self):
        """GrabCut参数标签页"""
        widget = QWidget()
        form = QFormLayout(widget)
        
        self.spin_grabcut_iter = QSpinBox()
        self.spin_grabcut_iter.setRange(config.GRABCUT_ITER_COUNT_MIN, config.GRABCUT_ITER_COUNT_MAX)
        self.spin_grabcut_iter.setValue(config.GRABCUT_ITER_COUNT)
        form.addRow("迭代次数:", self.spin_grabcut_iter)
        
        self.spin_grabcut_margin = QSpinBox()
        self.spin_grabcut_margin.setRange(config.GRABCUT_MARGIN_MIN, config.GRABCUT_MARGIN_MAX)
        self.spin_grabcut_margin.setValue(config.GRABCUT_MARGIN)
        form.addRow("边缘留白:", self.spin_grabcut_margin)
        
        self.spin_grabcut_morph = QSpinBox()
        self.spin_grabcut_morph.setRange(1, 31)
        self.spin_grabcut_morph.setSingleStep(2)
        self.spin_grabcut_morph.setValue(config.GRABCUT_MORPH_KERNEL_SIZE)
        form.addRow("形态学核大小:", self.spin_grabcut_morph)
        
        return widget
    
    def create_general_tab(self):
        """通用参数标签页"""
        widget = QWidget()
        form = QFormLayout(widget)
        
        self.spin_min_area = QSpinBox()
        self.spin_min_area.setRange(config.BOX_MIN_AREA_MIN, config.BOX_MIN_AREA_MAX)
        self.spin_min_area.setSingleStep(config.BOX_MIN_AREA_STEP)
        self.spin_min_area.setValue(config.BOX_MIN_AREA)
        form.addRow("最小框面积:", self.spin_min_area)
        
        self.double_nms = QDoubleSpinBox()
        self.double_nms.setRange(config.BOX_NMS_THRESHOLD_MIN, config.BOX_NMS_THRESHOLD_MAX)
        self.double_nms.setSingleStep(config.BOX_NMS_THRESHOLD_STEP)
        self.double_nms.setValue(config.BOX_NMS_THRESHOLD)
        form.addRow("NMS阈值:", self.double_nms)
        
        return widget
    
    def load_current_config(self):
        """加载当前配置到界面（编辑模式）"""
        # 设置默认保存路径（包含默认文件名）
        default_dir = self.get_default_config_dir()
        default_file = os.path.join(default_dir, "config.yaml")
        self.path_edit.setText(default_file)
    
    def browse_file(self):
        """浏览选择文件"""
        default_dir = self.get_default_config_dir()
        
        # 保存模式：选择保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存配置文件", default_dir, "YAML Files (*.yaml *.yml)"
        )
        
        if file_path:
            self.path_edit.setText(file_path)
    
    def get_config_dict(self):
        """获取当前界面配置为字典"""
        return {
            # 边缘检测
            "EDGE_CANNY_THRESHOLD1": self.spin_canny_t1.value(),
            "EDGE_CANNY_THRESHOLD2": self.spin_canny_t2.value(),
            "EDGE_GAUSSIAN_BLUR_SIZE": self.spin_edge_blur.value(),
            "EDGE_DILATE_ITERATIONS": self.spin_edge_dilate_iter.value(),
            "EDGE_DILATE_KERNEL_SIZE": self.spin_edge_dilate_kernel.value(),
            # 颜色分割
            "COLOR_KMEANS_K": self.spin_kmeans_k.value(),
            "COLOR_KMEANS_CRITERIA_EPS": self.spin_kmeans_eps.value(),
            "COLOR_KMEANS_CRITERIA_MAX_ITER": self.spin_kmeans_max_iter.value(),
            "COLOR_KMEANS_ATTEMPTS": self.spin_kmeans_attempts.value(),
            "COLOR_MORPH_OPEN_KERNEL_SIZE": self.spin_color_morph.value(),
            # MSER
            "MSER_DELTA": self.spin_mser_delta.value(),
            # OTSU
            "OTSU_BLUR_SIZE": self.spin_otsu_blur.value(),
            # GrabCut
            "GRABCUT_ITER_COUNT": self.spin_grabcut_iter.value(),
            "GRABCUT_MARGIN": self.spin_grabcut_margin.value(),
            "GRABCUT_MORPH_KERNEL_SIZE": self.spin_grabcut_morph.value(),
            # 通用参数
            "BOX_MIN_AREA": self.spin_min_area.value(),
            "BOX_NMS_THRESHOLD": self.double_nms.value(),
        }
    
    def get_default_config_dir(self):
        """获取默认配置文件夹路径"""
        default_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
        os.makedirs(default_dir, exist_ok=True)
        return default_dir
    
    def save_config(self):
        """保存配置到YAML文件"""
        file_path = self.path_edit.text().strip()
        
        # 如果路径为空或者是目录，使用默认文件名
        if not file_path or os.path.isdir(file_path):
            default_dir = self.get_default_config_dir()
            file_path = os.path.join(default_dir, "config.yaml")
        
        # 确保文件扩展名
        if not file_path.endswith(('.yaml', '.yml')):
            file_path += '.yaml'
        
        # 确保目标目录存在
        target_dir = os.path.dirname(file_path)
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
        
        try:
            config_data = self.get_config_dict()
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
            
            QMessageBox.information(self, "成功", f"配置已保存到:\n{file_path}")
            self.config_file_path = file_path
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败:\n{str(e)}")
