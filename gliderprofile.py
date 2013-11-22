from pylab import *
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
from mpl_toolkits.mplot3d import Axes3D
import netCDF4
import datetime as dt
import numpy as np
from simplekml import Kml,Style
import simplekml

#The URL for the data aggregation
#url = 'http://tds.gliders.ioos.us/thredds/dodsC/rutgers_salacia-20130916T1603_Time.ncml'
url = 'http://tds.gliders.ioos.us/thredds/dodsC/Rutgers-University_ru22-20130924T2010_Time.ncml'

#The Individual Files - doesn't work
#url = 'http://tds.gliders.ioos.us/thredds/dodsC/rutgers_salacia-20130916T1603_Files/salacia-20130921T134335_rt0.nc'

#Opens up all variables and prints
nc = netCDF4.Dataset(url).variables
print nc.keys()

#Chooses the variable
var = 'temperature'

#Chooses the bounds of acceptable values for the variable
bounds = [5,70]


################################################################################

#Opens up the shape of "Temperature" and the lon, lat, depth.
print [shape(nc[var]),shape(nc['lon']),shape(nc['lat']),shape(nc['depth'])]

#Finds the units
print nc['depth'].units
print nc[var].units

#Selects what time indicies to use
#indexused = [10,shape(nc['lat'])[0]-10]
indexused = [10,10000]
#indexused = [0,shape(nc['lat'])[0]]

#Slices the information needed
x = nc['lon'][indexused[0]:indexused[1]]
y = nc['lat'][indexused[0]:indexused[1]]
z = nc['depth'][indexused[0]:indexused[1]]
col = nc[var][indexused[0]:indexused[1]]

#Masks all values less than or equal to 0, or outside a given range
#http://docs.scipy.org/doc/numpy/reference/routines.ma.html
col = ma.masked_outside(col,bounds[0],bounds[1])
#col = ma.masked_less_equal(col,0)

#Does similar maksing for lat, long, depth.
x = ma.masked_outside(x,-180,180)
y = ma.masked_outside(y,-90,90)
z = ma.masked_outside(z,0,10000)

#How to show the compressed files - after masking?
col2 = col.compressed()

#Does the plotting and color transformation
#http://stackoverflow.com/questions/8931268/using-colormaps-to-set-color-of-line-in-matplotlib
#http://matplotlib.org/api/cm_api.html
jet = cm = plt.get_cmap('jet') 
cNorm  = colors.Normalize(vmin=col2.min(), vmax=col2.max(), clip=False)
scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
#print scalarMap.get_clim()
#print scalarMap.get_cmap()

colorVal = [[] for k in range(len(col))]
colorValHex = [[] for k in range(len(col))]
colorValHexKML = [[] for k in range(len(col))]
fig = plt.figure()
ax = fig.gca(projection='3d')
ax.invert_zaxis
for idx in range(len(col)):
    colorVal[idx] = scalarMap.to_rgba(col[idx])
    if (ma.getmask(col[idx]) == True):
        colorVal[idx] = (1,1,1,0)

    colorValHex[idx] = colors.rgb2hex(colorVal[idx])
    #print colorValHex[idx]
    colorValHexKML[idx] = simplekml.Color.hex(colorValHex[idx][1:7])
    #colorValHexKML[idx] = simplekml.Color.rgb(colorVal[idx][0],colorVal[idx][1],colorVal[idx][2],colorVal[idx][3])
    #print x[idx],y[idx],z[idx],col[idx],colorVal[idx]        
    #ax.scatter(x[idx], y[idx], z[idx], marker='o', c=colorVal, edgecolors='none')

#3D Plot
ax.scatter(x, y, z, marker='o', c=colorVal, edgecolors='none')
ax.invert_zaxis()
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_zlabel('Depth')
show()


#Converts to KML
kml = Kml()

#folder = kml.newfolder(name="Gliders")
#Defines the kmnl document name
kml.document.name = "GliderProfile"

#Makes a list of styles
stylelist = []
for i in range(len(col)-1):
    #if (ma.getmask(x[idx]) == False and ma.getmask(y[idx]) == False and 
    #    ma.getmask(z[idx]) == False and ma.getmask(col[idx]) == False):
    sharedstyle = Style()
    sharedstyle.linestyle.color = str(colorValHex[i]) 
    sharedstyle.linestyle.width = 10
    stylelist.append(sharedstyle)

#Looops over all
for i in range(len(col)-1):
    #if (ma.getmask(x[idx]) == False and ma.getmask(y[idx]) == False and 
    #    ma.getmask(z[idx]) == False and ma.getmask(col[idx]) == False):
    print x[i],y[i],colorValHexKML[i],-z[i]
    lin = kml.newlinestring(name='',description='',coords=[(x[i],y[i],-z[i]),(x[i+1],y[i+1],-z[i+1])])
    lin.style.linestyle.color = str(colorValHexKML[i])   #stylelist[i]
    lin.style.linestyle.width = 10  #50 pixels
    lin.altitudemode = simplekml.AltitudeMode.absolute
        
kml.save("C:\Users\john.tenhoeve\Documents\stest3.kml")
