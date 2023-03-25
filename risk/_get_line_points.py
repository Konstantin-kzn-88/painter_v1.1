# -----------------------------------------------------------
# Класс предназначен для получения массива координат ломанной линии
# по её вершинам
#
# (C) 2023 Kuznetsov Konstantin, Kazan , Russian Federation
# email kuznetsovkm@yandex.ru
# -----------------------------------------------------------

import numpy as np

class Polyline:
    """
    Класс предназначен для получения массива равноудаленных координат
    каждого отрезка ломанной линии по её вершинам
    """

    def __init__(self, points: list):
        '''
        :@param points: список точек 2-D ломанной линии ( например, [(x,y),(x1,y1),...,(xn,yn)] )
        '''
        self.points = points

    def _del_duplicates(self, seq):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]

    def get_all_coordinates(self):
        result=[]
        for i in range(len(self.points) - 1):
            # точки ломанной
            x1, x2 = self.points[i][0], self.points[i + 1][0]
            y1, y2 = self.points[i][1], self.points[i + 1][1]
            # расстояние
            dist = np.linalg.norm(np.array([x1,y1]) - np.array([x2,y2]))
            # количество точек
            num_point = int(dist)
            # итерполяция линейная
            x, y = np.linspace(x1, x2, num_point), np.linspace(y1, y2, num_point)
            # полученные точки сложив список
            result += [(a, b) for a, b in zip(x.astype(np.int64), y.astype(np.int64))]
        # уберем дубликаты и вернем список точек
        return self._del_duplicates(result)





if __name__ == '__main__':
    p = Polyline(points=[[1, 1], [5, 5], [10, 10]]).get_all_coordinates()
