import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import sys

from PySide6.QtCore import QObject, Signal, QRunnable
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton

POINTS = [(150, 150), (90, 90), (250, 330), (400, 300), (100, 250), (400, 100), (250, 400)]
SIZE_AREA = (500, 500)
POWER = 50


# def fmt(x, pos):
#     a, b = '{:.2e}'.format(x).split('e')
#     b = int(b)
#     return r'${} \times 10^{{{}}}$'.format(a, b)

class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(str)
    result = Signal(str)


class Worker(QRunnable):
    def __init__(self, size_area:tuple, point:tuple):
        super().__init__()
        self.signals = WorkerSignals()
        self.size_area = size_area
        self.point = point

    def run(self):
        try:
            print(f'точка{self.point}')
        except Exception as e:
            self.signals.error.emit(str(e))
        else:
            self.signals.finished.emit()
            self.signals.result.emit(f'точка{self.point} прошла в потоке')


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Воздействие точек")
        self.button = QPushButton("Расчет")
        self.button.clicked.connect(self.start_worker)
        self.setCentralWidget(self.button)

    def start_worker(self):
        print('hi')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

# plt.pcolor(result, cmap='jet')
# plt.colorbar(format=ticker.FuncFormatter(fmt))
# plt.show()
