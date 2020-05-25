# -*- coding: utf-8 -*-
"""
读取JAXA gsamp全球小时降水数据并绘制中国地区图, 时间为东八区北京时间。
Author: Limin Feng 
Email: fenglimin1993@gmail.com
"""

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib
import matplotlib.pyplot as plt
import matplotlib as mpl
import scipy.io as sio
import os
import time
import datetime
from datetime import datetime
from datetime import date
from datetime import timedelta
from matplotlib.font_manager import FontProperties
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
import matplotlib.cm as cm
import matplotlib.mlab as mlab
from matplotlib.ticker import MultipleLocator
import matplotlib.dates as mdates
from matplotlib.dates import AutoDateLocator, DateFormatter
from matplotlib.dates import DayLocator, HourLocator, DateFormatter, drange
from mpl_toolkits.basemap import Basemap
import netCDF4# pip install netCDF4
from netCDF4 import Dataset
import h5py# pip install h5py
import shapefile# pip install pyshp
import pathlib#pip install pathlib2
from pathlib import Path
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import warnings
warnings.filterwarnings('ignore')

matplotlib.rcParams['font.sans-serif'] = 'Times New Roman'
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['font.sans-serif'] = ['Times New Roman'] 
plt.rcParams['axes.unicode_minus']=False 
font = FontProperties(fname=r"C:\\Windows\\Fonts\\times.ttf") 

###########获取文件路径、文件名、后缀名############
def get_filename(filename):
  (filepath,tempfilename) = os.path.split(filename);
  (shotname,extension) = os.path.splitext(tempfilename);
  #return filepath, shotname, extension
  return shotname

################################################################################
# 字符串时间转换为计算机存储时间
def Normaltime1(datetime1):
	Normaltime = datetime.strptime(datetime1,'%Y-%m-%d %H_%M')
	return Normaltime

# datetime时间转为字符串
def Changestr(datetime1):
	str1 = datetime1.strftime('%Y-%m-%d %H:%M')
	return str1

path_Prec="data\Prec"

path=pathlib.Path(path_Prec)
fe=list(path.glob('**/gsmap*.dat'))

print(len(fe))

def read(filename):
	"""
	Args:
		filename: 文件名

	Returns:
		crain: 降水量mm <numpy.ndarray>
		gsamp: 雨量计数量 <numpy.ndarray>
	"""
	data = np.fromfile(filename, dtype="<f4")
	data = data.reshape((1200, 3600), order='C')[::-1]
	#gsamp = data[:440]
	#crain = data[440:]
	#return crain, gsamp
	return data

def get_lon_lat(lon, lat, lons, lats):
	lx=len(lon)
	ly=len(lat)
	minx,miny=min(lon),min(lat)#0, -90
	maxx,maxy=max(lon),max(lat)#360, 90
   #确定经纬度格点索引
	ny =int(ly*(maxy-lats)/(maxy-miny))#最大的纬度是第一个索引，绘图时上北下南
	#ny =int(ly*(maxy-lats)/(maxy-miny))#最小的纬度是第一个索引，绘图时上南下北
	nx=int(lx*(lons-minx)/(maxx-minx))
	return nx, ny
	
XDEF= np.arange(0.05,360,0.1)#0-180是东经，180-360对应着西经的180-0
#XDEF= np.arange(-179.95,180,0.1)#-180~180里头正的表示东经，负的表示西经
YDEF= np.arange(-59.95,60,0.1)#描述文件纬度范围
print(len(XDEF),len(YDEF))

cmap = mpl.colors.ListedColormap(["cyan", "darkcyan",
									"green", "lime",
									"yellow", "gold", "goldenrod",
									"darkred", "brown", "red",
									"darkviolet"])
cmap.set_over("indigo")
cmap.set_under('white')
bounds = [0.1, 0.5, 1, 2, 3, 4, 5, 6, 8, 10, 20, 40]
norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

llcrnrlat=10
urcrnrlat=60
llcrnrlon=70
urcrnrlon=140

for i in fe:
	crain = read(i)
	crain[crain==-99.0] = np.nan
	filename1=get_filename(i)
	filename2=filename1[12:26]
	TIME1=datetime.strptime(filename2,'%Y%m%d.%H%M')
	TIME=TIME1+timedelta(hours=8)
	StrTime=datetime.strftime(TIME,'%Y-%m-%d %H:%M')
	print(TIME)
	#print(StrTime)
	data=xr.Dataset({"Prec": (("lat","lon"), crain),},{"lon": XDEF,"lat": YDEF,"time": TIME},)
	
	Lons=data.lon
	Lats=data.lat
	Pr=data.Prec.values

	fig, ax = plt.subplots(1,1,figsize=(16,9), dpi= 300)

	m = Basemap(projection = 'merc', resolution='i', 
		llcrnrlon = llcrnrlon, llcrnrlat = llcrnrlat, urcrnrlon = urcrnrlon, urcrnrlat = urcrnrlat) 

	m.readshapefile('data\map\gadm36_CHN_1', 'states',drawbounds=True)

	x1, y1 = np.meshgrid(Lons, Lats) 
	x2, y2 = m(x1, y1)

	cs=m.pcolor(x2, y2, Pr,cmap=cmap, norm=norm)
	#m.drawlsmask(ocean_color='skyblue', land_color=(0, 0, 0, 0), lakes=True)
	m.drawparallels(np.arange(10,60,20),labels=[1,0,0,0], fontsize=18)
	m.drawmeridians(np.arange(70,140,20),labels=[0,0,0,1], fontsize=18)

	m.drawcoastlines()
	m.drawstates()
	m.drawcountries()

	cbar = m.colorbar(cs, extend="both", extendrect=True, ticks=bounds,
						extendfrac="auto", pad=0.01, shrink=0.8,
						aspect=40, fraction=0.01)
	
	cbar.ax.tick_params(labelsize=18)
	cbar.set_label('Precipitation (mm)',fontproperties=font,fontsize=24)

	TitleStr=str('China Precipitation at '+StrTime)
	plt.title(TitleStr,fontproperties=font,fontsize=28)
	plt.savefig(str(filename2)+'.png', dpi=300)
	plt.clf()
