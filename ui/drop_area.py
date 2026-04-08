from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from pathlib import Path


class DropArea(QWidget):
    file_dropped = pyqtSignal(str)
    status_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.label = QLabel("拖拽图片或PDF到此处")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 8px;
                padding: 40px;
                background: #f9f9f9;
                color: #666;
                font-size: 14px;
            }
            QLabel:hover {
                border-color: #0078d7;
                background: #f0f7ff;
                color: #0078d7;
            }
        """)
        layout.addWidget(self.label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
            self.label.setStyleSheet("""
                QLabel {
                    border: 2px dashed #0078d7;
                    background: #e6f3ff;
                    color: #0078d7;
                    padding: 40px;
                    border-radius: 8px;
                    font-size: 14px;
                }
            """)
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 8px;
                padding: 40px;
                background: #f9f9f9;
                color: #666;
                font-size: 14px;
            }
            QLabel:hover {
                border-color: #0078d7;
                background: #f0f7ff;
                color: #0078d7;
            }
        """)

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.file_dropped.emit(file_path)
            self.status_changed.emit(f"已选择: {Path(file_path).name}")
