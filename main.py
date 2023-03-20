import numpy as np
from scipy.signal import fftconvolve
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def fmt(x, pos):
    a, b = '{:.2e}'.format(x).split('e')
    b = int(b)
    return r'${} \times 10^{{{}}}$'.format(a, b)

points = np.array([[150, 150], [90, 90], [250, 330], [400, 300], [100, 250], [400, 100], [250, 400]])
width, height = 500, 500
im = np.zeros((width, height))
im[points[:, 1], points[:, 0]] = 1.0  # set points
x = np.arange(0, 201)
y = np.arange(0, 201)
X, Y = np.meshgrid(x, y)
distance = ((X - 100) ** 2 + (Y - 100) ** 2) ** .5
power = 1 - distance / 100
power[power < 0] = 0  # cut off power function
power = power / np.sum(power)  # normalization
result = fftconvolve(im, power, mode='same')  # convolutions
plt.pcolor(result, cmap='jet')
plt.colorbar(format=ticker.FuncFormatter(fmt))
plt.savefig('foo.png')

