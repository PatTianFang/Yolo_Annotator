from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QInputDialog, QMenu
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPixmap
import os

class ClassManager(QWidget):
    class_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.classes = []
        self.colors = []
        
        # 设置窗口图标（如果作为独立窗口）
        self.set_window_icon()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.list_widget)
    
    def set_window_icon(self):
        """设置窗口图标"""
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "logo.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
    def load_classes(self, classes, colors):
        self.classes = classes
        self.colors = colors
        self.list_widget.clear()
        for i, cls in enumerate(self.classes):
            color = self.colors[i % len(self.colors)]
            item = QListWidgetItem(cls)
            
            # 创建颜色图标
            pixmap = QPixmap(16, 16)
            pixmap.fill(QColor(*color))
            item.setIcon(QIcon(pixmap))
            
            self.list_widget.addItem(item)
            
    def show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return
            
        menu = QMenu(self)
        edit_action = menu.addAction("编辑")
        delete_action = menu.addAction("删除")
        
        action = menu.exec(self.list_widget.mapToGlobal(pos))
        row = self.list_widget.row(item)
        
        if action == edit_action:
            new_name, ok = QInputDialog.getText(self, "编辑类别", "新类别名称:", text=self.classes[row])
            if ok and new_name.strip():
                self.classes[row] = new_name.strip()
                item.setText(self.classes[row])
                self.class_changed.emit()
                
        elif action == delete_action:
            self.list_widget.takeItem(row)
            del self.classes[row]
            self.class_changed.emit()
