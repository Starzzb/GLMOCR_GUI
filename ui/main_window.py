from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QProgressBar,
    QMessageBox,
    QFileDialog,
    QLabel,
    QApplication,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMimeData
from PyQt5.QtGui import QImage, QPixmap
from pathlib import Path
import tempfile

from ui.drop_area import DropArea
from ui.result_viewer import ResultViewer
from core.file_validator import FileValidator
from core.recognizer import GLMRecognizer


class RecognitionThread(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, recognizer: GLMRecognizer, file_path: str):
        super().__init__()
        self.recognizer = recognizer
        self.file_path = file_path

    def run(self):
        try:
            result = self.recognizer.recognize(self.file_path)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.recognizer = GLMRecognizer()
        self._current_result = None
        self._temp_files = []
        self._init_ui()
        self._init_styles()
        self._init_clipboard_listener()

    def _init_clipboard_listener(self):
        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_V and event.modifiers() == Qt.ControlManager:
            self._paste_image()
        else:
            super().keyPressEvent(event)

    def _paste_image(self):
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        if mime_data.hasImage():
            image = clipboard.image()
            if not image.isNull():
                temp_path = tempfile.mktemp(suffix=".png")
                image.save(temp_path)
                self._temp_files.append(temp_path)
                self._update_status("已从剪贴板粘贴图片")
                self._start_recognition(temp_path)
                return True
        elif mime_data.hasUrls():
            urls = mime_data.urls()
            if urls:
                file_path = urls[0].toLocalFile()
                self._update_status(f"已从剪贴板粘贴: {Path(file_path).name}")
                self._start_recognition(file_path)
                return True
        return False

    def _init_ui(self):
        self.setWindowTitle("GLM-OCR 拖拽识别工具")
        self.setMinimumSize(900, 600)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        top_layout = QHBoxLayout()
        self.drop_area = DropArea()
        self.drop_area.file_dropped.connect(self._on_file_dropped)
        self.drop_area.status_changed.connect(self._update_status)
        top_layout.addWidget(self.drop_area, stretch=2)

        btn_layout = QVBoxLayout()
        self.btn_browse = QPushButton("浏览文件")
        self.btn_browse.clicked.connect(self._browse_file)
        self.btn_paste = QPushButton("粘贴图片")
        self.btn_paste.clicked.connect(self._paste_image)
        self.btn_clear = QPushButton("清空")
        self.btn_clear.clicked.connect(self._clear_result)
        self.btn_export = QPushButton("导出结果")
        self.btn_export.clicked.connect(self._export_result)
        self.btn_export.setEnabled(False)

        for btn in [self.btn_browse, self.btn_paste, self.btn_clear, self.btn_export]:
            btn.setFixedHeight(40)
            btn_layout.addWidget(btn)
        btn_layout.addStretch()
        top_layout.addLayout(btn_layout, stretch=1)

        layout.addLayout(top_layout)

        self.result_view = ResultViewer()
        layout.addWidget(self.result_view)

        self.status_label = QLabel("就绪")
        self.progress = QProgressBar()
        self.progress.setVisible(False)

        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress)
        layout.addLayout(status_layout)

    def _init_styles(self):
        self.setStyleSheet("""
            QMainWindow { background: #ffffff; }
            QPushButton {
                background: #0078d7;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover { background: #005a9e; }
            QPushButton:disabled { background: #ccc; }
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: #0078d7;
                width: 10px;
            }
        """)

    def _on_file_dropped(self, file_path: str):
        valid, error = FileValidator.validate(file_path)
        if not valid:
            QMessageBox.warning(self, "格式错误", error)
            return

        self._start_recognition(file_path)

    def _browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", "图片与PDF (*.jpg *.jpeg *.png *.pdf)"
        )
        if file_path:
            self._on_file_dropped(file_path)

    def _start_recognition(self, file_path: str):
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.status_label.setText("识别中...")
        self.btn_export.setEnabled(False)

        self.thread = RecognitionThread(self.recognizer, file_path)
        self.thread.finished.connect(self._on_recognition_done)
        self.thread.error.connect(self._on_recognition_error)
        self.thread.start()

    def _on_recognition_done(self, result: dict):
        self.progress.setVisible(False)
        self.status_label.setText("识别完成")
        self.result_view.set_markdown(result["markdown"])
        self._current_result = result
        self.btn_export.setEnabled(True)

    def _on_recognition_error(self, error_msg: str):
        self.progress.setVisible(False)
        self.status_label.setText("识别失败")
        QMessageBox.critical(self, "识别错误", f"识别过程出错:\n{error_msg}")

    def _clear_result(self):
        self.result_view.clear()
        self.status_label.setText("已清空")
        self.btn_export.setEnabled(False)

    def _export_result(self):
        if not self._current_result:
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存结果",
            "glm_ocr_result.md",
            "Markdown文件 (*.md);;文本文件 (*.txt);;JSON文件 (*.json)",
        )
        if not save_path:
            return

        try:
            if save_path.endswith(".json"):
                import json

                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(self._current_result, f, ensure_ascii=False, indent=2)
            else:
                content = (
                    self._current_result["markdown"]
                    if save_path.endswith(".md")
                    else self._current_result["raw_text"]
                )
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(content)
            self.status_label.setText(f"已导出: {Path(save_path).name}")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", str(e))

    def _update_status(self, msg: str):
        self.status_label.setText(msg)
