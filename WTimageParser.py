import os
import subprocess
import time
import sys
import string
import re
from Tkinter import *
import Image, ImageTk, ImageOps

from svgDebug import *

# C:/Program\ Files\ \(x86\)/SoftSoft/WinTopo/Topo.exe -oFolder:c:/temp/svg_create_tmp -oASC -oPNG -thr:0 -pru:10 -tZS c:/mikee/python/artbot/test/ns2c_small.JPG

WTexe = "C:/Program Files (x86)/SoftSoft/WinTopo/Topo.exe"

maxWid = 600
maxHei = 600


def createImageData(imagePath, workingDir, origImgWin, procImgWin,
                    despec, despecVal):
   """Given arguments about the import image and how to process it,
   simplify and resize it, pass it to wintopo for images processing and vectorisation"""
   
   # show original image in window
   im = Image.open(imagePath)
   im=ImageOps.fit(im, (int(origImgWin.config()["width"][4]), int(origImgWin.config()["height"][4])), Image.ANTIALIAS)
   photIm = ImageTk.PhotoImage(im)
   origImgWin.label = photIm
   origImgWin.create_image((0, 0), image=photIm, anchor=NW)
   
   # convert image to svg
   vecFile, wid, hei = convertImageToVectorFormat(imagePath, workingDir, procImgWin,
                                                  despec, despecVal)
                               
   # convert image data to path data
   svgW, svgH, pathData = convertVectorFormatToLines(vecFile)
   
   return wid, hei, svgW, svgH, pathData
   
   
##########################################################################
# Turn image into wintopo vector file

def convertImageToVectorFormat(imagePath, workingDir, procImgWin,
                               despec, despecVal):
   # convert chosen file to png and resize
   im = Image.open(imagePath)
   filename = os.path.basename(imagePath)
   base = filename.split('.')[0]
   pngInputFile = os.path.join(workingDir, base+".png")
   
   wid, hei = im.size
   print "input image size =", wid, "hei =", hei
   
   if wid > maxWid or hei > maxHei:
      imgScale = min(maxWid/float(wid), maxHei/float(hei))
      print "scale =", imgScale, "new image size wid =", imgScale*wid, "hei =", imgScale*hei
      # filter = NEAREST, BILINEAR, BICUBIC, ANTIALIAS 
      im = im.resize((int(imgScale*wid), int(imgScale*hei)), Image.ANTIALIAS)
      wid, hei = im.size
      print "resize pic size w=", wid, " h=", hei
   
   im.save(pngInputFile)
   
   # build switches
   despecSw = "-des:" + str(despecVal)
   
   # create command line and launch
   wtCmd = [WTexe, "-oFolder:"+workingDir]
   wtCmd.append("-eCN") # canny edge detection with defaults
   if despec: wtCmd.append(despecSw)
   wtCmd.extend(["-oPNG", "-oTXT"])
   
   wtCmd.append(pngInputFile)
   print "about to exe: '" + str(wtCmd) + "'"
   subprocess.call(wtCmd)
   
   # show processed image in window
   im = Image.open(os.path.join(workingDir, base +".png"))
   im=ImageOps.fit(im, (int(procImgWin.config()["width"][4]), int(procImgWin.config()["height"][4])), Image.ANTIALIAS)
   photIm = ImageTk.PhotoImage(im)
   procImgWin.label = photIm
   procImgWin.create_image((0, 0), image=photIm, anchor=NW)
   
   return os.path.join(workingDir, base +".txt"), wid, hei



##########################################################################
# Turn svg into lines
   
def convertVectorFormatToLines(vecPath):
   #global lineData
   
   wtContents = []
   lineData = []
   with open(vecPath, 'r') as f:
      wtContents = f.readlines()

   # POLYLINE, sequential polyline identifier, polyline length, number of vertices, Z level/height, minimum X, minimum Y, maximum X, maximum Y, colour, layer, reserved value
   # After this the polyline vertex coordinates are listed out, with the X and Y coordinate of each vertex per line. 
   # X coordinate, Y coodinate
   # If there is an arc in the polyline then the arc details follow vertex coordinates on the same line. 
   # X coordinate, Y coodinate, ARC, X centre, Y centre, Radius, Bulge
   # The word END terminates each polyline. 

   foundPl = False
   maxX = 0.0
   maxY = 0.0
   for wtL in wtContents:
      match = re.match(r'POLYLINE', wtL)
      if match:
         foundPl = True
         px = 0.0
         py = 0.0
         continue
      if foundPl:
         if re.match(r'END', wtL):
            foundPl = False
            continue
         polybits = wtL.split(', ')
         x = float(polybits[0])
         y = float(polybits[1])
         maxX = max(maxX, x)
         maxY = max(maxY, y)
         if px == 0.0 and py == 0.0:
            px = x
            py = y
         else:
            lineData.append([px, py, x, y])
            px = x
            py = y
         # ignore arcs for now

   #traverseSvg(svgDoc, svgH)
   #svgDbg.add("finished converting to lines")
   
   return maxX, maxY, lineData
   
   