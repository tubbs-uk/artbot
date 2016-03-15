import os
import subprocess
import time
import sys
from Tkinter import *

# PIL imports
# import Image, ImageTk, ImageOps

# Pillow imports
from PIL import Image, ImageTk, ImageOps

import svgConverter
import botOptions
from svgDebug import *



potraceDir = "c:/mikee/tools/potrace-1.13.win64"

maxWid = 600
maxHei = 600


def createImageData(imagePath, origImgWin, procImgWin):
   """Given arguments about the import image and how to process it,
   simplify and resize it, and trace it to svg"""
   # show original image in window
   im = Image.open(imagePath)
   inWid =  im.size[0]
   inHei =  im.size[1]
   winWid = int(origImgWin.config()["width"][4])
   winHei = int(origImgWin.config()["height"][4])
   im.thumbnail((winWid, winHei))

   im.save(os.path.join(botOptions.workingDir, "resized.png"), "PNG")

   outWidth = im.size[0]
   outHeight = im.size[1]
   print "max width: " + str(winWid) + ", max height: " + str(winHei) + ", given width: " + str(inWid) + ", given height: " + str(inHei) + ", got width: " + str(outWidth) + ", got height: " + str(outHeight)
   photIm = ImageTk.PhotoImage(im)
   origImgWin.label = photIm
   origImgWin.create_image((0, 0), image=photIm, anchor=NW)
   
   # convert image to svg
   svgFile, wid, hei = convertImageToSvg(imagePath, procImgWin)
                               
   # convert image data to path data
   svgW, svgH, pathData = svgConverter.convertSvgToLines(svgFile)
   
   return wid, hei, svgW, svgH, pathData
   
   
##########################################################################
# Turn image into svg

def convertImageToSvg(imagePath, procImgWin):
   # convert chosen file to pgm and resize
   im = Image.open(imagePath)
   filename = os.path.basename(imagePath)
   base = filename.split('.')[0]
   pgmInputFile = os.path.join(botOptions.workingDir, base+".pgm")
   
   wid, hei = im.size
   print "input image size =", wid, "hei =", hei
   
   if wid > maxWid or hei > maxHei:
      imgScale = min(maxWid/float(wid), maxHei/float(hei))
      print "scale =", imgScale, "new image size wid =", imgScale*wid, "hei =", imgScale*hei
      # filter = NEAREST, BILINEAR, BICUBIC, ANTIALIAS 
      im = im.resize((int(imgScale*wid), int(imgScale*hei)), Image.ANTIALIAS)
      wid, hei = im.size
      print "resize pic size w=", wid, " h=", hei
    
   im.save(pgmInputFile)
   
   # pass pgm file to mkbitmap
   mkBmCmd = [os.path.join(potraceDir, "mkbitmap.exe")]
   pgmOutputFile = os.path.join(botOptions.workingDir, base +"_masked.pgm")
   mkBmCmd.extend(["-o", pgmOutputFile])
   
   if botOptions.getScaleOn():
      mkBmCmd.extend(["-s", botOptions.getScaleVal()])
      
   if botOptions.getInterpolationType() == 1:
      mkBmCmd.append("-1")
   else:
      mkBmCmd.append("-3")
      
   if botOptions.getThreshOn() == 1:
      mkBmCmd.extend(["-t", botOptions.getThreshVal()])
      
   if botOptions.getFilterOn() == 1:
      mkBmCmd.extend(["-f", botOptions.getFilterVal()])
   else:
      mkBmCmd.append("-n")

   # TODO use blur value

   if botOptions.getInvertOn() == 1:
      mkBmCmd.append("-i")
      
   mkBmCmd.append(pgmInputFile)
   #print "tracecmd =", mkBmCmd
   subprocess.call(mkBmCmd)
   
   # show processed image in window
   im = Image.open(pgmOutputFile)
   im=ImageOps.fit(im, (int(procImgWin.config()["width"][4]), int(procImgWin.config()["height"][4])), Image.ANTIALIAS)
   photIm = ImageTk.PhotoImage(im)
   procImgWin.label = photIm
   procImgWin.create_image((0, 0), image=photIm, anchor=NW)
   
   # pass output pgm to potrace to create svg
   ptCmd = [os.path.join(potraceDir, "potrace.exe"), "-s", "-o"]
   svgOut = os.path.join(botOptions.workingDir, base +".svg")
   ptCmd.extend([svgOut, pgmOutputFile])
   subprocess.call(ptCmd)
   
   return svgOut, wid, hei


