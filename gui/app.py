from __future__ import annotations

from pathlib import Path


def run_gui() -> None:
    try:
        from PySide6.QtWidgets import (
            QApplication,
            QLabel,
            QMainWindow,
            QPushButton,
            QTextEdit,
            QVBoxLayout,
            QWidget,
        )
    except ImportError as exc:
        raise RuntimeError(
            "PySide6 is required for the GUI. Install with: python -m pip install -e .[gui]"
        ) from exc

    class MainWindow(QMainWindow):
        def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle("SysML v2 Transfer Toolkit")
            self.resize(900, 640)

            self.input_editor = QTextEdit()
            self.output_editor = QTextEdit()
            self.output_editor.setReadOnly(True)

            self.convert_code_button = QPushButton("代码 -> 图形")
            self.convert_graphics_button = QPushButton("图形 -> 代码")

            self.convert_code_button.clicked.connect(self.convert_code)
            self.convert_graphics_button.clicked.connect(self.convert_graphics)

            layout = QVBoxLayout()
            layout.addWidget(QLabel("输入文本"))
            layout.addWidget(self.input_editor)
            layout.addWidget(self.convert_code_button)
            layout.addWidget(self.convert_graphics_button)
            layout.addWidget(QLabel("输出结果"))
            layout.addWidget(self.output_editor)

            container = QWidget()
            container.setLayout(layout)
            self.setCentralWidget(container)

        def convert_code(self) -> None:
            from core import code_to_graphics

            text = self.input_editor.toPlainText()
            result = code_to_graphics(text)
            self.output_editor.setPlainText(str(result))

        def convert_graphics(self) -> None:
            from core import graphics_to_code

            text = self.input_editor.toPlainText()
            model = {"content": text}
            result = graphics_to_code(model)
            self.output_editor.setPlainText(result)

    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
