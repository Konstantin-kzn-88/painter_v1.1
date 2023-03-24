import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from risk import risk_allocation


def fmt(x, pos):
    a, b = '{:.2e}'.format(x).split('e')
    b = int(b)
    return r'${} \times 10^{{{}}}$'.format(a, b)


points = [(30, 30), (60, 60), (90, 90), (120, 120),(150, 150)]
size_area = (500, 500)
power_risk = 100
result = 0

for point in points:
    result += risk_allocation.Allocation(point, size_area, power_risk).calculation()


plt.pcolor(result, cmap='jet')
plt.colorbar(format=ticker.FuncFormatter(fmt))
plt.show()
