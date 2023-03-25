import numpy as np
from scipy.signal import fftconvolve
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from PIL import Image, ImageDraw
lines=((10, 20), (50,10))
points=np.array([[150,150],[90,90], [250,330], [400,300], [100,250],[400,100],[250,400]])
width, height = 500,500
im = Image.new('1', (width, height), (0))
draw = ImageDraw.Draw(im)
draw.line(xy=lines, fill='white')  #draw line
im=np.asarray(im, dtype=np.uint8)
#im=np.zeros((width, height))
im[points[:,1], points[:,0]]=1.0 # set points
x=np.arange(0, 201)
y=np.arange(0, 201)
X,Y=np.meshgrid(x,y)
distance=((X-100)**2+(Y-100)**2)**.5
power=1-distance/100
power[power<0]=0 # cut off power function
my_cmap = ListedColormap(["#ffffff", "#ff00ff", '#0000ff', '#00ff00', "#00ff00",
                       '#00ffff', '#00ffff', '#ffff00', '#ffff00', '#ff0000'])
result=fftconvolve(im, power, mode='same') # convolutions
plt.pcolor(result, cmap='jet')
# plt.colorbar(format=ticker.FuncFormatter(fmt))
plt.savefig('foo.png')