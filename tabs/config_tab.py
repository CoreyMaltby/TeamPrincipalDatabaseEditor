from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QStackedWidget, QHBoxLayout


class ConfigTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Layout
        main_layout = QVBoxLayout(self)

        # Left tab
        button_layout = QHBoxLayout()
        self.buttons = []
        button_names = [
            "Dirty Air",
            "Tyres",
            "Pitstops",
            "Incidents",
            "Safety Car",
            "Injuries"
        ]

        for i, name in enumerate(button_names):
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, idx=i: self.switch_page(idx))
            button_layout.addWidget(btn)
            self.buttons.append(btn)

        button_layout.addStretch()
        main_layout.addLayout(button_layout, 1)

        # Right tab
        self.stack = QStackedWidget()
        self.stack.addWidget(self.make_page("Dirty Air"))
        self.stack.addWidget(self.make_page("Tyres"))
        self.stack.addWidget(self.make_page("Pitstops"))
        self.stack.addWidget(self.make_page("Incidents"))
        self.stack.addWidget(self.make_page("Safety Car"))
        self.stack.addWidget(self.make_page("Injuries"))

        main_layout.addWidget(self.stack, 3)

    def make_page(self, text: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel(text))
        layout.addStretch()
        return page

    def switch_page(self, index: int):
        self.stack.setCurrentIndex(index)