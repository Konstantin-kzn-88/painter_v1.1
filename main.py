import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import sys
import time
from shapely.geometry import LineString, Polygon, Point

from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton

# Координаты объектов
OBJECTS = [(10, 10), (2500, 2500), (500, 2500), (2500, 2700, 1000, 1500), (300, 300, 300, 500, 500, 500, 500, 300)]
# Типы объектов
# 0 - линия
# 1 - многоугольник
# 2 - точка
TYPE_OBJECTS = [2, 2, 2, 0, 1]
# Площадь картинки
SIZE_AREA = (3628, 3211)
# Сила риска для каждого объекта
POWER = [100, 100, 100, 100, 100]
# Размер анализируемой сетки
SIZE_SEARCH = 50


# def fmt(x, pos):
#     a, b = '{:.2e}'.format(x).split('e')
#     b = int(b)
#     return r'${} \times 10^{{{}}}$'.format(a, b)

class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(str)
    result = Signal(str)


class Worker(QRunnable):
    def __init__(self, size_area: tuple, obj_points: tuple, obj_type: int):
        super().__init__()
        self.signals = WorkerSignals()
        self.size_area = size_area
        self.obj_points = obj_points
        self.obj_type = obj_type

    def run(self):
        try:
            # посмотрим к каким областям относится рассматриваемы объект
            # разобьем площадь картинки на квадраты поиска на квадраты поиска
            x_line = [i for i in range(0, self.size_area[0] + 1, SIZE_SEARCH)].append(self.size_area[0]%SIZE_SEARCH)
            y_line = [i for i in range(0, self.size_area[1] + 1, SIZE_SEARCH)].append(self.size_area[1]%SIZE_SEARCH)

            print(f'Объект: {self.obj_points}')
            time.sleep(3)
        except Exception as e:
            self.signals.error.emit(str(e))
        else:
            self.signals.finished.emit()
            self.signals.result.emit(f'объект  {self.obj_points} прошел в потоке')


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Воздействие точек")
        self.button = QPushButton("Расчет")
        self.button.clicked.connect(self.start_worker)
        self.setCentralWidget(self.button)

        # е. Пул потоков
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(len(OBJECTS))
        print(f'Число потоков {self.threadpool.maxThreadCount()}')

    def start_worker(self):
        for OBJECT in OBJECTS:
            worker = Worker(SIZE_AREA, OBJECT, POWER[OBJECTS.index(OBJECT)])
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
