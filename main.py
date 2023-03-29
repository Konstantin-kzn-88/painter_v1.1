import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import sys
import time
from shapely.geometry import LineString, Polygon, Point

from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton

# Координаты объектов
# OBJECTS = [(10, 10), (2500, 2500), (500, 2500), (2500, 2700, 1000, 1500), (300, 300, 300, 500, 500, 500, 500, 300)]
OBJECTS = [(10, 10), ]
# Типы объектов
# 0 - линия
# 1 - многоугольник
# 2 - точка
TYPE_OBJECTS = [2, 2, 2, 0, 1]
# Площадь картинки
SIZE_AREA = (628, 211)
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
    def __init__(self, size_area: tuple, obj_points: tuple, obj_type: int, power: int):
        super().__init__()
        self.signals = WorkerSignals()
        self.size_area = size_area
        self.obj_points = obj_points
        self.obj_type = obj_type
        self.power = power

    def run(self):
        try:
            # Создадим объект до которого идет измерение
            if len(self.obj_points) > 2:
                if self.obj_type == 0:  # линейный объект
                    print('линейный')
                    obj = LineString(list(zip(self.obj_points[0::2], self.obj_points[1::2])))
                else:
                    print('стационарный')
                    obj = Polygon(list(zip(self.obj_points[0::2], self.obj_points[1::2])))
            else:
                print('точка')
                obj = Point(self.obj_points[0], self.obj_points[1])
            # посмотрим к каким областям относится рассматриваемы объект
            # разобьем площадь картинки на квадраты поиска на квадраты поиска
            x_line = [i for i in range(0, self.size_area[0] + 1, SIZE_SEARCH)]
            y_line = [i for i in range(0, self.size_area[1] + 1, SIZE_SEARCH)]

            find_coordinate = []

            for x in x_line:
                for y in y_line:
                    search_point = (x, y, x + SIZE_SEARCH, y, x + SIZE_SEARCH, y + SIZE_SEARCH, x, y + SIZE_SEARCH)
                    search_polygon = Polygon(list(zip(search_point[0::2], search_point[1::2])))
                    distance = search_polygon.distance(obj)
                    if distance < self.power:
                        find_coordinate.extend(search_point)


            print(f'Координаты: {find_coordinate}')
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
            worker = Worker(SIZE_AREA, OBJECT, TYPE_OBJECTS[OBJECTS.index(OBJECT)], POWER[OBJECTS.index(OBJECT)])
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
