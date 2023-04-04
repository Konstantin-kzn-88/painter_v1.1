import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import sys
from shapely.geometry import LineString, Polygon, Point

from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton

# Координаты объектов
OBJECTS = [(500, 100), (400, 200), (250, 500), (100, 150, 300, 300), (500, 500, 500, 400, 400, 400, 400, 500)]

# Типы объектов
# 0 - линия
# 1 - многоугольник
# 2 - точка
TYPE_OBJECTS = [2, 2, 2, 0, 1]
# Площадь картинки
SIZE_AREA = (640, 640)
# Сила воздействия для каждого объекта
POWER = [100, 200, 100, 100, 130]
# Размер анализируемой сетки
SIZE_SEARCH_STEP_1 = 50
SIZE_SEARCH_STEP_2 = 10
SIZE_SEARCH_STEP_3 = 2
SIZE_SEARCH_STEP_4 = 1


def fmt(x, pos):
    '''
    Функция что бы у графика была в шкала в "10 в степени"
    '''
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

    def search_nearby(self, x_min: int, x_max: int, y_min: int, y_max: int, size_search: int,
                      object_under_study) -> list:
        '''
        Функция поиска близлежащих координат
        :param x_min: - мин.координата области поиска по Х
        :param x_max: - макс.координата области поиска по Х
        :param y_min: - мин.координата области поиска по Y
        :param y_max: - макс.координата области поиска по Y
        :param size_search: - размер квадратов на которые происходит разбивка
        :param object_under_study: - исследуемый объект (LineString, Polygon, Point)
        :return: result_square - спосок координат близлежащих к объекту квадратов
        '''
        x_line = [i for i in range(x_min, x_max + 1, size_search)]
        y_line = [i for i in range(y_min, y_max + 1, size_search)]
        result_square = []
        for x in x_line:
            for y in y_line:
                search_point = (x, y, x + size_search, y, x + size_search, y + size_search, x, y + size_search)
                search_polygon = Polygon(list(zip(search_point[0::2], search_point[1::2])))
                distance = search_polygon.distance(object_under_study)
                if distance < self.power:
                    result_square.extend(search_point)
        return result_square

    def run(self):
        try:
            # создадим силу воздействия
            dist_power = [i for i in range(self.power)]
            power = list(reversed([i / 100 for i in dist_power]))
            # нулевая матрица
            zeors_array = np.zeros((self.size_area[0], self.size_area[1]))
            # Создадим объект до которого идет измерение
            if len(self.obj_points) > 2:
                if self.obj_type == 0:  # линия
                    obj = LineString(list(zip(self.obj_points[0::2], self.obj_points[1::2])))
                else:  # многоугольник
                    obj = Polygon(list(zip(self.obj_points[0::2], self.obj_points[1::2])))
            else:  # точка
                obj = Point(self.obj_points[0], self.obj_points[1])
            # ШАГ 1.
            # разобъем область на квадраты по 50 пикселей и определим близлежащие к объекту
            find_square_50 = self.search_nearby(x_min=0, x_max=self.size_area[0], y_min=0, y_max=self.size_area[1],
                                                size_search=SIZE_SEARCH_STEP_1, object_under_study=obj)
            # ШАГ 2.
            print(f'Шаг №2 {self.obj_points}')
            find_square_10 = []
            for i in range(0, len(find_square_50), 8):
                # Получим координаты квадратов по 50 пикселей и снова их разобъем на
                # квадраты по 10 пикселей и определим близлежащие
                sq = find_square_50[i:i + 8]

                # разобьем квадраты 50 на квадраты по 10
                result_square = self.search_nearby(x_min=sq[0], x_max=sq[2], y_min=sq[1], y_max=sq[5],
                                                   size_search=SIZE_SEARCH_STEP_2, object_under_study=obj)
                find_square_10.extend(result_square)

            # ШАГ 3.
            print(f'Шаг №3 {self.obj_points}')
            find_square_2 = []
            for i in range(0, len(find_square_10), 8):
                # Получим координаты квадратов по 10 пикселей и снова их разобъем на
                # квадраты по 2 пикселя и определим близлежащие
                sq = find_square_10[i:i + 8]
                # разобьем квадраты 10 на квадраты по 2
                result_square = self.search_nearby(x_min=sq[0], x_max=sq[2], y_min=sq[1], y_max=sq[5],
                                                   size_search=SIZE_SEARCH_STEP_3, object_under_study=obj)
                find_square_2.extend(result_square)
            # # ШАГ 4.
            print(f'Шаг №4 {self.obj_points}')
            find_coordinate_step_4 = []
            for i in range(0, len(find_square_2), 8):
                sq = find_square_2[i:i + 8]
                # Пройдемся по квадратам find_square_2 и опредлим какие точки в них
                # будут близлежащими к объекту
                x_line = [i for i in range(sq[0], sq[2] + 1, SIZE_SEARCH_STEP_4)]
                y_line = [i for i in range(sq[1], sq[5] + 1, SIZE_SEARCH_STEP_4)]
                for x in x_line:
                    for y in y_line:
                        search_point = Point(x, y)
                        find_coordinate_step_4.append(search_point)
            # Удалим повторы точек и посчитаем в какой точке какое воздействие
            print(f'Шаг удаление {self.obj_points}')
            for item in list(set(find_coordinate_step_4)):
                distance = int(item.distance(obj))
                if distance == 0:
                    zeors_array[int(item.x), int(item.y)] = max(power)
                else:
                    if int(distance) in dist_power:
                        ind = dist_power.index(int(distance) - 1)
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
        print("Поток завершен!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


