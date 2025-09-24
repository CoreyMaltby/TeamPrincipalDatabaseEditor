
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget

# Tab imports (stubs for now)
from tabs.config_tab import ConfigTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Team Principal Manager - Data Editor")
        self.resize(1000, 600)

        tab_widget = QTabWidget()
        tab_widget.addTab(ConfigTab(), "Config")

        self.setCentralWidget(tab_widget)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
