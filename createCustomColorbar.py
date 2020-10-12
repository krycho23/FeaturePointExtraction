import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from matplotlib import pylab as pl
from matplotlib.colors import ListedColormap

data = np.random.rand(6,6)
fig = pl.figure(1)
fig.clf()
ax = fig.add_subplot(1,1,1)
img = ax.imshow(data, interpolation='nearest', vmin=0.5, vmax=0.99)
fig.colorbar(img)

fig, ax = plt.subplots(figsize=(6, 1))
fig.subplots_adjust(bottom=0.5)

cmap = mpl.cm.cool
norm = mpl.colors.Normalize(vmin=5, vmax=10)

cb1 = mpl.colorbar.ColorbarBase(ax, cmap=cmap,
                                norm=norm,
                                orientation='horizontal')
cb1.set_label('Some Units')
fig.show()

error_map = np.asarray([[1,5,11],
                        [5,9,21],
                        [1,3,11]])

cmap = mpl.colors.ListedColormap([ 'red', 'white', 'green'])

np.random.seed(42)
data = error_map
fig, ax = plt.subplots(figsize=(20, 10))
heatmap = ax.pcolor(data, cmap=cmap)

#legend
cbar = plt.colorbar(heatmap)
cbar.ax.set_yticklabels(['$<2$','', '', '$>2$','', '', '$>10$'])

plt.show()



