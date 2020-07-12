import cv2
from cv2 import VideoWriter,VideoWriter_fourcc,imread,resize
import os
import pathlib#pip install pathlib2
from pathlib import Path

def get_filename(filename):
  (filepath,tempfilename) = os.path.split(filename);
  (shotname,extension) = os.path.splitext(tempfilename);
  #return filepath, shotname, extension
  return shotname
  
img_root="D:\\Test_data\\2020\\Prec_Fig\\"

path=pathlib.Path(img_root)
fe=list(path.glob('**/20*.jpg'))

print(len(fe))

#Edit each frame's appearing time!
fps=4
fourcc=VideoWriter_fourcc(*"MJPG")
videoWriter=cv2.VideoWriter("China_Prec_2020-01_06.avi",fourcc,fps,(1920,1080))

#im_names=os.listdir(img_root)
#im_names=
for im_name in fe:
	frame=cv2.imread(img_root+get_filename(im_name)+'.jpg')
	print (im_name)
	videoWriter.write(frame)
	
videoWriter.release()
