# -----------------------------------------------------------
# Класс предназначен для получения массива координат ломанной линии
# по её вершинам
#
# (C) 2023 Kuznetsov Konstantin, Kazan , Russian Federation
# email kuznetsovkm@yandex.ru
# -----------------------------------------------------------

import numpy as np
from scipy.signal import fftconvolve


class Polyline:
    """
    Класс предназначен для получения массива координат ломанной линии
    по её вершинам
    """

    def __init__(self, points: list):
        '''

        :@param points: список точек 2-D ломанной линии ( например, [[x,y],[x1,y1],...,[xn,yn] )
        :@param size_area: размер исследуемой области, pixel (например, (width, height))
        :@param power_risk: сила воздействия точек, pixel
        '''
        self.points = points

    def get_all_coordinates(self):
        result = []
        for i in range(len(self.points) - 1):
            print(self.points[i], self.points[i + 1])
            # Получим коэффициеты прямой
            k = (self.points[i][1] - self.points[i + 1][1]) / (self.points[i][0] - self.points[i + 1][0])
            b = self.points[i + 1][1] - k * self.points[i + 1][0]
            # Получим все координаты прячмой по 2 точкам




if __name__ == '__main__':
    p = Polyline(points=[[1, 1], [5, 5], [10, 10]]).get_all_coordinates()
