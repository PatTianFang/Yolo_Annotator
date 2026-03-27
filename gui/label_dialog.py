from PySide6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QLineEdit, QPushButton, QHBoxLayout
from PySide6.QtGui import QIcon
import os

class LabelDialog(QDialog):
    def __init__(self, class_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择标签")
        self.class_list = class_list
        self.selected_class = None
        
        # 设置窗口图标
        self.set_window_icon()

        layout = QVBoxLayout(self)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入新标签或搜索...")
        layout.addWidget(self.search_edit)

        self.list_widget = QListWidget()
        self.list_widget.addItems(self.class_list)
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton("确定")
        self.btn_cancel = QPushButton("取消")
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

        self.btn_ok.clicked.connect(self.accept_label)
        self.btn_cancel.clicked.connect(self.reject)
        self.list_widget.itemDoubleClicked.connect(self.accept_label)
        self.search_edit.returnPressed.connect(self.accept_label)
    
    def set_window_icon(self):
        """设置窗口图标"""
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "logo.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def accept_label(self):
        text = self.search_edit.text().strip()
        if not text:
            selected_items = self.list_widget.selectedItems()
            if selected_items:
                text = selected_items[0].text()
        if text:
            self.selected_class = text
            self.accept()

    def get_class(self):
        return self.selected_class
