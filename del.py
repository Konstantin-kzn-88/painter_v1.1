import numpy as np
import matplotlib.pyplot as plt

# Создаем массив точек
points = np.array([[1,3], ])

width, height = 10, 10
# Создаем массив 0
im = np.zeros((width, height))
# Устанавливаем 1 в массив im с идексами points
im[points[:, 1], points[:, 0]] = 1.0  # Где про это почитать что это такое?
# print(im)

x = np.arange(0, 10)
y = np.arange(0, 10)
X, Y = np.meshgrid(x, y)
print(Y)

zs = np.sqrt(X**2 + Y**2)

h = plt.contourf(X, Y, zs)
plt.axis('scaled')
plt.colorbar()
plt.show()