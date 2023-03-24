# -----------------------------------------------------------
# Класс предназначен для расчета распредления риска
#
# (C) 2023 Kuznetsov Konstantin, Kazan , Russian Federation
# email kuznetsovkm@yandex.ru
# -----------------------------------------------------------

import numpy as np
from scipy.signal import fftconvolve

class Allocation:
    """
    Класс предназначен для расчета распредления риска
    """

    def __init__(self, points: list, size_area: tuple, power_risk: int):
        '''

        :@param points: список точек 2-D ( например, [(x,y),(x1,y1),...,(xn,yn)] )
        :@param size_area: размер исследуемой области, pixel (например, (width, height))
        :@param power_risk: сила воздействия точек, pixel
        '''
        self.points = points
        self.size_area = size_area
        self.power_risk = power_risk

    def calculation(self):
        points = np.array([self.points, ])
        width, height =  self.size_area
        im = np.zeros((width, height))
        im[points[:, 1], points[:, 0]] = 1.0  # set points

        x = np.arange(0, self.power_risk*2)
        y = np.arange(0, self.power_risk*2)
        X, Y = np.meshgrid(x, y)
        distance = ((X - 100) ** 2 + (Y - 100) ** 2) ** .5
        power = 1 - distance / 100
        power[power < 0] = 0  # cut off power function
        power = power / np.sum(power)  # normalization
        result = fftconvolve(im, power, mode='same')  # convolutions

        return  result

