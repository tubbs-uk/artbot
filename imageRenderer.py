from Tkinter import *
import sys
import time

from svgDebug import *

class ImageRenderer:
   def __init__(self, imgW, imgH, svgW, svgH):   
      self.m_imgW = imgW
      self.m_imgH = imgH
      self.m_svgW = svgW
      self.m_svgH = svgH

   def createWinAndDrawLineData(self, lineData):

      # create a window and canvas to put the line in
      self.svgRenderWin = Tk()
      self.svgRenderCanv = Canvas(self.svgRenderWin, width=self.m_svgW, height=self.m_svgH)
      self.svgRenderCanv.pack()

      # go through each line and draw it in the canvas
      lineno = 0
      for line in lineData:
         lineno += 1
         self.svgRenderCanv.create_line(line[0], self.m_imgH-line[1], line[2], self.m_imgH-line[3], tags="line"+str(lineno))
         if not lineno % 100:
            self.svgRenderWin.update()

   def updateLine(self, line, lineno, lineType, drawConnectors):
      connector = False
      if lineType == 'C':
         col="blue"
         connector = True
      else:
         col="red"
         
      if not connector or (connector and drawConnectors):
         self.svgRenderCanv.create_line(line[0], self.m_imgH-line[1], line[2], self.m_imgH-line[3], fill=col)
