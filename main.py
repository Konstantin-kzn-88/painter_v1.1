import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from risk import risk_allocation, _get_line_points


def fmt(x, pos):
    a, b = '{:.2e}'.format(x).split('e')
    b = int(b)
    return r'${} \times 10^{{{}}}$'.format(a, b)


line = [[50, 50], [200, 200], [400, 400]]
line_coords = _get_line_points.Polyline(line).get_all_coordinates()
size_area = (500, 500)
power_risk = 100
result = 0

for point in line_coords:
    result += risk_allocation.Allocation(point, size_area, power_risk).calculation()

result = result / (0.5*len(line_coords))
points = [[300, 300], [400, 400]]

for point in points:
    result += risk_allocation.Allocation(point, size_area, power_risk).calculation()


plt.pcolor(result, cmap='jet')
plt.colorbar(format=ticker.FuncFormatter(fmt))
plt.show()