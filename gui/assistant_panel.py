from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QSpinBox, QDoubleSpinBox, QComboBox, QPushButton, QGroupBox
from PySide6.QtCore import Qt, Signal
import config

class AssistantPanel(QWidget):
    # 触发执行的信号
    # 参数：(模式名称字符串, 参数字典)
    run_requested = Signal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # 模式选择
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["边缘检测", "颜色分割", "显著性检测", "MSER提取", "Otsu二值化", "GrabCut前景"])
        self.combo_mode.currentIndexChanged.connect(self.on_mode_changed)
        
        mode_layout = QFormLayout()
        mode_layout.addRow("检测模式:", self.combo_mode)
        layout.addLayout(mode_layout)

        # 参数配置 GroupBox
        self.group_params = QGroupBox("参数配置")
        self.form_params = QFormLayout(self.group_params)
        
        # -- 边缘检测参数 --
        self.spin_canny_t1 = QSpinBox()
        self.spin_canny_t1.setRange(config.EDGE_CANNY_THRESHOLD_MIN, config.EDGE_CANNY_THRESHOLD_MAX)
        self.spin_canny_t1.setValue(config.EDGE_CANNY_THRESHOLD1)
        
        self.spin_canny_t2 = QSpinBox()
        self.spin_canny_t2.setRange(config.EDGE_CANNY_THRESHOLD_MIN, config.EDGE_CANNY_THRESHOLD_MAX)
        self.spin_canny_t2.setValue(config.EDGE_CANNY_THRESHOLD2)
        
        # -- 颜色分割参数 --
        self.spin_kmeans_k = QSpinBox()
        self.spin_kmeans_k.setRange(config.COLOR_KMEANS_K_MIN, config.COLOR_KMEANS_K_MAX)
        self.spin_kmeans_k.setValue(config.COLOR_KMEANS_K)

        # -- MSER 参数 --
        self.spin_mser_delta = QSpinBox()
        self.spin_mser_delta.setRange(config.MSER_DELTA_MIN, config.MSER_DELTA_MAX)
        self.spin_mser_delta.setValue(config.MSER_DELTA)
        
        # -- Otsu 参数 --
        self.spin_otsu_blur = QSpinBox()
        self.spin_otsu_blur.setRange(config.OTSU_BLUR_SIZE_MIN, config.OTSU_BLUR_SIZE_MAX)
        self.spin_otsu_blur.setSingleStep(config.OTSU_BLUR_SIZE_STEP)
        self.spin_otsu_blur.setValue(config.OTSU_BLUR_SIZE)

        # -- GrabCut 参数 --
        self.spin_grabcut_iter = QSpinBox()
        self.spin_grabcut_iter.setRange(config.GRABCUT_ITER_COUNT_MIN, config.GRABCUT_ITER_COUNT_MAX)
        self.spin_grabcut_iter.setValue(config.GRABCUT_ITER_COUNT)
        
        self.spin_grabcut_margin = QSpinBox()
        self.spin_grabcut_margin.setRange(config.GRABCUT_MARGIN_MIN, config.GRABCUT_MARGIN_MAX)
        self.spin_grabcut_margin.setValue(config.GRABCUT_MARGIN)
        
        # -- 通用参数 --
        self.spin_min_area = QSpinBox()
        self.spin_min_area.setRange(config.BOX_MIN_AREA_MIN, config.BOX_MIN_AREA_MAX)
        self.spin_min_area.setValue(config.BOX_MIN_AREA)
        self.spin_min_area.setSingleStep(config.BOX_MIN_AREA_STEP)
        
        self.double_nms = QDoubleSpinBox()
        self.double_nms.setRange(config.BOX_NMS_THRESHOLD_MIN, config.BOX_NMS_THRESHOLD_MAX)
        self.double_nms.setValue(config.BOX_NMS_THRESHOLD)
        self.double_nms.setSingleStep(config.BOX_NMS_THRESHOLD_STEP)

        layout.addWidget(self.group_params)

        # 执行按钮
        self.btn_run = QPushButton("执行辅助标注")
        self.btn_run.clicked.connect(self.on_run_clicked)
        layout.addWidget(self.btn_run)
        
        # 初始化显示正确的参数
        self.on_mode_changed(0)

    def on_mode_changed(self, idx):
        # 清空当前表单
        while self.form_params.count():
            item = self.form_params.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                
        mode = self.combo_mode.currentText()
        if mode == "边缘检测":
            self.form_params.addRow("Canny 阈值1:", self.spin_canny_t1)
            self.form_params.addRow("Canny 阈值2:", self.spin_canny_t2)
        elif mode == "颜色分割":
            self.form_params.addRow("聚类数(K):", self.spin_kmeans_k)
        elif mode == "显著性检测":
            pass # 无特殊参数
        elif mode == "MSER提取":
            self.form_params.addRow("MSER Delta:", self.spin_mser_delta)
        elif mode == "Otsu二值化":
            self.form_params.addRow("高斯核大小:", self.spin_otsu_blur)
        elif mode == "GrabCut前景":
            self.form_params.addRow("迭代次数:", self.spin_grabcut_iter)
            self.form_params.addRow("边缘留白:", self.spin_grabcut_margin)
            
        # 通用参数始终显示
        self.form_params.addRow("最小面积:", self.spin_min_area)
        self.form_params.addRow("NMS阈值:", self.double_nms)

    def on_run_clicked(self):
        mode_text = self.combo_mode.currentText()
        mode_map = {
            "边缘检测": "edge",
            "颜色分割": "color",
            "显著性检测": "saliency",
            "MSER提取": "mser",
            "Otsu二值化": "otsu",
            "GrabCut前景": "grabcut"
        }
        
        params = {
            "min_area": self.spin_min_area.value(),
            "nms_threshold": self.double_nms.value(),
            "canny_t1": self.spin_canny_t1.value(),
            "canny_t2": self.spin_canny_t2.value(),
            "kmeans_k": self.spin_kmeans_k.value(),
            "mser_delta": self.spin_mser_delta.value(),
            "otsu_blur": self.spin_otsu_blur.value(),
            "grabcut_iter": self.spin_grabcut_iter.value(),
            "grabcut_margin": self.spin_grabcut_margin.value()
        }
        
        self.run_requested.emit(mode_map.get(mode_text, "edge"), params)
