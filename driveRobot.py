import sys
import angleData
import json
import math
import serial
import time
import re
import math
import threading
from svgDebug import *
import botOptions



class SerialWrapper:
   def __init__(self):
      self.m_serObj = None

   def activateSerial(self):
      if not botOptions.getSerialOn() or self.m_serObj:
         return

      #serialPort = r'\\.\COM15'
      serialPort = r'\\.\\' + botOptions.getSerialVal()
      baudRate = 9600
      byteSize = serial.EIGHTBITS
      serParity = serial.PARITY_NONE
      stopBits = serial.STOPBITS_ONE
      serTimeout = 10

      self.m_serObj = serial.Serial(port=serialPort, baudrate=baudRate, bytesize=byteSize, parity=serParity, stopbits=stopBits, timeout=serTimeout)


   def write(self, s):
      if not botOptions.getSerialOn(): return
      self.m_serObj.write(s)
      
   def readline(self):
      if not botOptions.getSerialOn(): return ""
      return self.m_serObj.readline()
   
   
   
class RobotDriver:

   def __init__(self, gui, svgW, svgH, lines):
      self.m_lines = lines
      self.m_svgW = svgW
      self.m_svgH = svgH
      self.m_maxSvgDimen = max(svgW, svgH)
      self.m_gui = gui
      self.m_lineTimes = []

      # starts with pen up
      self.penIsUp = True

      # try and estimate time to either raise or lower pen (in ms)
      self.m_movePenTime = 100
      
      # 10,000ms drives for 405mm
      # so 5,000ms should go 202.5mm (approx length of A4)
      self.m_fullLengthMSecs = 1800
      #self.m_fullRotationMSecs = 11811
      self.m_fullRotationMSecs = 2985
            
      self.m_ser = SerialWrapper()
      
      
      
   # convert angle in degrees (0 - 360) into number of miiliseconds to rotate for
   def ang2ms(self, ang):
      return (int)((math.fabs(ang)/360.0) * self.m_fullRotationMSecs)
   
   def calcAngleTime(self, newang, oldang):
      calcang = newang - oldang
      if calcang > 180.0:
         calcang -= 360.0
      elif calcang < -180.0:
         calcang += 360.0
      
      return (calcang, self.ang2ms(calcang))

   def doTurn(self, ang, angMs): 
      #svgDbg.add("doTurn args: ang='" + str(ang) + "', angMs='" + str(angMs) + "'")
      # default direction anti-clockwise
      dir = 'A'
      dirTxt = "anticlockwise"
      if ang < 0.0:
         # if angle negative, turn clockwise
         dir = 'C'
         dirTxt = "clockwise"
      
      svgDbg.add("Turning " + dirTxt + " " + str(ang) + " degress (" + str(angMs) + "ms)")
      self.m_ser.write(dir + str(angMs) + '\n')
   
      self.m_ser.readline()
      # finished turning now

   # convert distance in units (0 - m_maxSvgDimen) into number of miiliseconds to drive forward for
   # dist will be some number related to the size of the svg
   def dist2MSecs(self, dist):
      return (int)((dist/self.m_maxSvgDimen) * self.m_fullLengthMSecs)
   
   def doLine(self, distMs):
      svgDbg.add("Moving for " + str(distMs) + "ms")
      self.m_ser.write('F' + str(distMs) + '\n')
   
      self.m_ser.readline()
      # finished doing line now

   # return time take to move pen
   def penUp(self):
      if self.penIsUp:
         return 0

      svgDbg.add("Raising pen to " + botOptions.getPenUpVal())
      self.m_ser.write('P' + botOptions.getPenUpVal() + '\n')

      self.m_ser.readline()
      self.penIsUp = True
      return self.m_movePenTime

   # return time take to move pen
   def penDown(self):
      if not self.penIsUp:
         return 0

      svgDbg.add("Lowering pen to " + botOptions.getPenDownVal())
      self.m_ser.write('P' + botOptions.getPenDownVal() + '\n')

      self.m_ser.readline()
      self.penIsUp = False
      return self.m_movePenTime
      
   def conv2Angs(self, line, lastAng):
      angleDistData = angleData.cartesianToPolar(line)
         
      calcang, angleMs = self.calcAngleTime(angleDistData[1], lastAng)            
      lastAng = angleDistData[1]
      distMs = self.dist2MSecs(angleDistData[0])
                  
      self.m_totMs += angleMs
      self.m_totMs += distMs
      svgDbg.add("converted to angle " + str(calcang) + ", angleMs " + str(angleMs) + " and distMs " + str(distMs))
      
      return calcang, angleMs, distMs, lastAng

   def calculateTimes(self):
      lineno = 0
      lastAng = 0.0
      # try and sort lines into order with connected lines closest to each other (possibly not much diff to original order)
      # SEEMS TO TAKE LONGER TO DRAW!
      #self.m_lines.sort(key=lambda tot: sum(tot))
      
      totLines = len(self.m_lines)
      if totLines < 1:
         return

      self.m_totMs = 0
      totZangs = 0

      # add an implicit first line going from 0,0 to the start of the first line
      # to allow the robot to start at the bottom of the page pointing up and drive to it's first point
      prevLine = [0, 0, 0, 0]

      for line in self.m_lines:
         lineno += 1
         svgDbg.add("looking at orig line " + str(lineno) + "/" + str(totLines) + ": " + str(line))
         

         if len(prevLine) != 0 and prevLine[2] != line[0] and prevLine[3] != line[1]:
            # create a line linking the previous endpoint with the new startpoint (if different)
            svgDbg.add("adding connection between " + str(prevLine) + " and " + str(line))
            
            # add time in to account for raising and lowering the pen
            self.m_totMs += (self.m_movePenTime * 2)
            
            # create a line which starts where the last one ended, and ends where the new one starts
            connectLine = [prevLine[2], prevLine[3], line[0], line[1]]
            
            calcang, angleMs, distMs, lastAng = self.conv2Angs(connectLine, lastAng)
            if angleMs == 0:
               totZangs += 1
               svgDbg.add("zero angle")
                   
            # 'C' means this is a connecting line, not part of the drawing
            self.m_lineTimes.append(['C', connectLine, calcang, angleMs, distMs])
         else:
            svgDbg.add("not adding connector as first line, or start same as end")
                     
         prevLine = line
         
         
         calcang, angleMs, distMs, lastAng = self.conv2Angs(line, lastAng)
         if angleMs == 0:
            totZangs += 1
            svgDbg.add("zero angle")
         
         # 'L' line means this line is part of the drawing, not a connecting movement
         self.m_lineTimes.append(['L', line, calcang, angleMs, distMs])
         
         
      svgDbg.add("total time to print: " + str(self.m_totMs) + "ms. Total zero angles " + str(totZangs)+ "\n")
      return self.m_totMs

   def driveRobot(self):
      lineno = 0
      totLines = len(self.m_lineTimes)
      timeDone = 0

      self.m_ser.activateSerial()
      
      # set pause/resume buttons up in gui
      if self.m_gui:
         self.m_gui.setButtonsOn(True)
      
      for line in self.m_lineTimes:
         lineno += 1
         svgDbg.add("----------------")
         svgDbg.add("looking at line " + str(lineno) + "/" + str(totLines) + ": " + str(line))
         
         self.doTurn(line[2], line[3])
         timeDone += line[3]
         
         if line[0] == 'C':
            svgDbg.add("CONNECTOR")
            timeDone += self.penUp()

         elif line[0] == 'L':
            svgDbg.add("LINE")
            timeDone += self.penDown()
         
         self.doLine(line[4])
         timeDone += line[4]
         

         #winUpdate = False
         #if not lineno % 1000: winUpdate = True
         if self.m_gui:
            pauseBtnPushed = self.m_gui.updateRobotLine(line[0], line[1], lineno, totLines, timeDone, self.m_totMs)
            while pauseBtnPushed:
               time.sleep(1)
               # pauseBtnPushed() will return False when resume pushed
               pauseBtnPushed = self.m_gui.pauseBtnPushed()
                  
      # drawing done. Set pause/resume buttons off
      if self.m_gui: self.m_gui.setButtonsOff()
      
   def sendToRobot(self):
      # thread code, will return from constuctor after calling these and new thread will do processing in background
      self.m_thread = threading.Thread(target=self.internalThreadRoutine)
      self.m_thread.start()

   def internalThreadRoutine(self):
      #self.calculateTimes()   
      self.driveRobot()
      # will exit thread when finished
      

def passLinesToRobot(gui, svgW, svgH, lines):
   #svgDbg.add("given lines: " + str(lines))

   # this will create a thread to handle the meat of the function and return immediately
   robot = RobotDriver(gui, svgW, svgH, lines)
   
   
   
   
   
class ThreadedWrapper:

   def __init__(self, master):
   
      self.m_master = master
      self.m_queue = Queue.Queue()
      
      self.m_gui = CreateSvgApp(master, self.m_queue)
      
      self.m_running = True
      self.m_thread = threading.Thread(target=self.threadLoop)
      self.m_thread.start()
      self.periodicCall()
      
   def periodicCall(self):
      self.m_master.after(200, self.periodicCall)
      self.m_gui.processIncoming()
      print "periodicCall"
      if not self.m_running:
         import sys
         exit(1)
         
   def threadLoop(self):
      while self.m_running:
         time.sleep(1)
           
   

if __name__ == "__main__":
   
   if len(sys.argv) <= 1:
      print "no file arg passed in"
      sys.exit()
      
   # as test read in file arg
   with open(sys.argv[1], 'r') as f:
      lineData = f.readlines()

   passLinesToRobot(None, lineData)
