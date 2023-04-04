import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def fmt(x, pos):
    '''
    Функция что бы у графика была в шкала в "10 в степени"
    '''
    a, b = '{:.2e}'.format(x).split('e')
    b = int(b)
    return r'${} \times 10^{{{}}}$'.format(a, b)

OBJECTS = [(500, 100), (400, 200), (250, 500), (100, 150, 300, 300), (500, 500, 500, 400, 400, 400, 400, 500)]
# Сила воздействия для каждого объекта
POWER = [100, 200, 100, 100, 100]

w,h=640,640
res=np.zeros((w,h))
for item in OBJECTS:
    im=np.zeros((w,h), dtype=np.uint8)
    if len(item)==2:
        im[item]=255
    elif len(item)==4:
        cv2.line(im,item[0:2],item[2:4],(255,),1)
    else:
        cv2.fillPoly(im,[np.array(item).reshape(-1,1,2)],(255,))
    im=~im
    dist=cv2.distanceTransform(im, distanceType=cv2.DIST_L2, maskSize=cv2.DIST_MASK_PRECISE)
    dist=(POWER[OBJECTS.index(item)]-dist)/POWER[OBJECTS.index(item)]
    dist=np.clip(dist, 0,1)
    res+=dist
# plt.imshow(res, cmap='jet', vmin=0, vmax=1)
# plt.gca().invert_yaxis()
# plt.colorbar()
plt.pcolor(res, cmap='jet')
plt.colorbar(format=ticker.FuncFormatter(fmt))
plt.show()
