import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import sys
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
SIZE_AREA = (628, 628)
# Сила риска для каждого объекта
POWER = [100, 100, 100, 100, 100]
# Размер анализируемой сетки
SIZE_SEARCH_STEP_1 = 50
SIZE_SEARCH_STEP_2 = 10
SIZE_SEARCH_STEP_3 = 2
SIZE_SEARCH_STEP_4 = 1


def fmt(x, pos):
    a, b = '{:.2e}'.format(x).split('e')
    b = int(b)
    return r'${} \times 10^{{{}}}$'.format(a, b)

class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(str)
    result = Signal(np.ndarray)


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
            # создадим силу
            dist_power = [i for i in range(self.power)]
            power = list(reversed([i / 100 for i in dist_power]))
            print(dist_power)
            print(power)
            # нулевая матрица
            zeors_array = np.zeros((self.size_area[0], self.size_area[1]))
            # Создадим объект до которого идет измерение
            if len(self.obj_points) > 2:
                if self.obj_type == 0:  # линейный объект
                    # print('линейный')
                    obj = LineString(list(zip(self.obj_points[0::2], self.obj_points[1::2])))
                else:
                    # print('стационарный')
                    obj = Polygon(list(zip(self.obj_points[0::2], self.obj_points[1::2])))
            else:
                # print('точка')
                obj = Point(self.obj_points[0], self.obj_points[1])
            # посмотрим к каким областям относится рассматриваемы объект
            # разобьем площадь картинки на квадраты поиска на квадраты поиска
            x_line = [i for i in range(0, self.size_area[0] + 1, SIZE_SEARCH_STEP_1)]
            y_line = [i for i in range(0, self.size_area[1] + 1, SIZE_SEARCH_STEP_1)]

            find_coordinate_step_1 = []

            for x in x_line:
                for y in y_line:
                    search_point = (x, y, x + SIZE_SEARCH_STEP_1, y, x + SIZE_SEARCH_STEP_1, y + SIZE_SEARCH_STEP_1, x,
                                    y + SIZE_SEARCH_STEP_1)
                    search_polygon = Polygon(list(zip(search_point[0::2], search_point[1::2])))
                    distance = search_polygon.distance(obj)
                    if distance < self.power:
                        find_coordinate_step_1.extend(search_point)

            # print(f'Координаты 1: {find_coordinate_step_1}')
            find_coordinate_step_2 = []
            for i in range(0, len(find_coordinate_step_1), 8):
                sq = find_coordinate_step_1[i:i + 8]
                # разобьем площадь картинки на квадраты поиска на квадраты поиска
                x_line = [i for i in range(sq[0], sq[2] + 1, SIZE_SEARCH_STEP_2)]
                y_line = [i for i in range(sq[1], sq[5] + 1, SIZE_SEARCH_STEP_2)]
                for x in x_line:
                    for y in y_line:
                        search_point = (
                            x, y, x + SIZE_SEARCH_STEP_2, y, x + SIZE_SEARCH_STEP_2, y + SIZE_SEARCH_STEP_2, x,
                            y + SIZE_SEARCH_STEP_2)
                        search_polygon = Polygon(list(zip(search_point[0::2], search_point[1::2])))
                        distance = search_polygon.distance(obj)
                        if distance < self.power:
                            find_coordinate_step_2.extend(search_point)

            # print(f'Координаты 2: {find_coordinate_step_2}')
            find_coordinate_step_3 = []
            for i in range(0, len(find_coordinate_step_2), 8):
                sq = find_coordinate_step_2[i:i + 8]
                # разобьем площадь картинки на квадраты поиска на квадраты поиска
                x_line = [i for i in range(sq[0], sq[2] + 1, SIZE_SEARCH_STEP_3)]
                y_line = [i for i in range(sq[1], sq[5] + 1, SIZE_SEARCH_STEP_3)]
                for x in x_line:
                    for y in y_line:
                        search_point = (
                            x, y, x + SIZE_SEARCH_STEP_3, y, x + SIZE_SEARCH_STEP_3, y + SIZE_SEARCH_STEP_3, x,
                            y + SIZE_SEARCH_STEP_3)
                        search_polygon = Polygon(list(zip(search_point[0::2], search_point[1::2])))
                        distance = search_polygon.distance(obj)
                        if distance < self.power:
                            find_coordinate_step_3.extend(search_point)
            # print(f'Координаты 3: {find_coordinate_step_3}')

            find_coordinate_step_4 = []
            for i in range(0, len(find_coordinate_step_3), 8):
                sq = find_coordinate_step_3[i:i + 8]
                # разобьем площадь картинки на квадраты поиска на квадраты поиска
                x_line = [i for i in range(sq[0], sq[2] + 1, SIZE_SEARCH_STEP_4)]
                y_line = [i for i in range(sq[1], sq[5] + 1, SIZE_SEARCH_STEP_4)]
                # print(x_line)
                # print(y_line)
                # print(20*'-')
                for x in x_line:
                    for y in y_line:
                        # print(f'x = {x}, y = {y}')
                        search_point = Point(x, y)
                        find_coordinate_step_4.append(search_point)


            i =0
            l = len(list(set(find_coordinate_step_4)))
            for item in list(set(find_coordinate_step_4)):
                distance = int(item.distance(obj))
                print(f'distance = {distance}, i={i}, l={l}')
                i+=1
                if distance == 0:
                    zeors_array[int(item.x), int(item.y)] = max(power)
                else:
                    if int(distance) in dist_power:
                        ind = dist_power.index(int(distance)-1)
                        zeors_array[int(item.x), int(item.y)] = power[ind]
                    if distance == 0:
                        zeors_array[int(item.x), int(item.y)] = max(power)



        except Exception as e:
            self.signals.error.emit(str(e))
        else:
            self.signals.finished.emit()
            self.signals.result.emit(zeors_array)


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

        # ж. Матрица heatmap'а
        self.heatmap = 0

    def start_worker(self):
        for OBJECT in OBJECTS:
            worker = Worker(SIZE_AREA, OBJECT, TYPE_OBJECTS[OBJECTS.index(OBJECT)], POWER[OBJECTS.index(OBJECT)])
            worker.signals.result.connect(self.worker_output)
            worker.signals.finished.connect(self.worker_complete)
            self.threadpool.start(worker)

    def worker_output(self, s):
        self.heatmap = self.heatmap + s
        if self.threadpool.activeThreadCount() == 0:
            plt.pcolor(self.heatmap, cmap='jet')
            plt.colorbar(format=ticker.FuncFormatter(fmt))
            plt.show()

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
