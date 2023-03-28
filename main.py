import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import sys
import time

from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton

POINTS = [(10, 10), (400, 400), (300, 300), (500, 500), (100, 10),  (10, 50),]
SIZE_AREA = (503, 503)
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
    def __init__(self, size_area: tuple, point: tuple):
        super().__init__()
        self.signals = WorkerSignals()
        self.size_area = size_area
        self.point = point

    def run(self):
        try:
            print(f'точка{self.point}')
            time.sleep(3)
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

        # е. Пул потоков
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(len(POINTS))
        print(f'Число потоков {self.threadpool.maxThreadCount()}')

    def start_worker(self):
        for POINT in POINTS:
            worker = Worker(SIZE_AREA, POINT)
            worker.signals.result.connect(self.worker_output)
            worker.signals.finished.connect(self.worker_complete)
            self.threadpool.start(worker)

    def worker_output(self, s):
        print(s)

    def worker_complete(self):
        print("THREAD COMPLETE!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

# plt.pcolor(result, cmap='jet')
# plt.colorbar(format=ticker.FuncFormatter(fmt))
# plt.show()
