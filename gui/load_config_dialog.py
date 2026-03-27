from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QLineEdit, QLabel, QMessageBox, QListWidget
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
import yaml
import os


class LoadConfigDialog(QDialog):
    """加载配置对话框 - 用于选择并加载YAML配置文件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_file_path = None
        self.loaded_config = None
        self.setWindowTitle("加载配置")
        self.resize(500, 400)
        
        # 设置窗口图标
        self.set_window_icon()
        
        self.init_ui()
        self.refresh_config_list()
    
    def set_window_icon(self):
        """设置窗口图标"""
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "logo.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 配置文件列表
        layout.addWidget(QLabel("可用的配置文件:"))
        self.config_list = QListWidget()
        self.config_list.itemClicked.connect(self.on_config_selected)
        self.config_list.itemDoubleClicked.connect(self.on_config_double_clicked)
        layout.addWidget(self.config_list)
        
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
        
        # 加载按钮
        load_btn = QPushButton("加载配置")
        load_btn.clicked.connect(self.load_config)
        layout.addWidget(load_btn)
    
    def get_default_config_dir(self):
        """获取默认配置文件夹路径"""
        default_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
        os.makedirs(default_dir, exist_ok=True)
        return default_dir
    
    def refresh_config_list(self):
        """刷新配置文件列表"""
        self.config_list.clear()
        config_dir = self.get_default_config_dir()
        
        if os.path.exists(config_dir):
            for filename in sorted(os.listdir(config_dir)):
                if filename.endswith(('.yaml', '.yml')):
                    self.config_list.addItem(filename)
    
    def on_config_selected(self, item):
        """当从列表中选择配置时"""
        config_dir = self.get_default_config_dir()
        file_path = os.path.join(config_dir, item.text())
        self.path_edit.setText(file_path)
    
    def on_config_double_clicked(self, item):
        """双击配置文件直接加载"""
        self.on_config_selected(item)
        self.load_config()
    
    def browse_file(self):
        """浏览选择文件"""
        default_dir = self.get_default_config_dir()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择配置文件", default_dir, "YAML Files (*.yaml *.yml)"
        )
        
        if file_path:
            self.path_edit.setText(file_path)
    
    def load_config(self):
        """从YAML文件加载配置"""
        file_path = self.path_edit.text().strip()
        if not file_path:
            QMessageBox.warning(self, "警告", "请选择配置文件！")
            return
        
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "警告", "文件不存在！")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            if not config_data:
                QMessageBox.warning(self, "警告", "配置文件为空！")
                return
            
            self.config_file_path = file_path
            self.loaded_config = config_data
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载配置失败:\n{str(e)}")
    
    def get_loaded_config(self):
        """获取加载的配置数据"""
        return self.loaded_config
