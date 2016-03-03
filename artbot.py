from svgDebug import *
import imageParser
import WTimageParser
from imageRenderer import *
from driveRobot import *
from notebook import *

from Tkinter import *
import ttk
from ScrolledText import *
import tkFileDialog
import os
import sys
import threading
import Queue
import time

workingDir = "c:/temp/svg_create_tmp"
dumpLineData = True

if os.path.exists(workingDir) == False:
    os.makedirs(workingDir)


class CreateSvgApp:
    def __init__(self, master):

        self.m_renderWin = None
        self.m_master = master
        self.m_robotDriveProgress = 0
        self.m_paused = False

        # choose file button
        controlBtnsFrame = Frame(master)
        controlBtnsFrame.pack(side=TOP)

        self.fileLabelVar = StringVar()
        self.fileLabelVar.set("No file")
        self.fileLabel = Label(controlBtnsFrame, textvariable=self.fileLabelVar, justify=LEFT)
        self.fileLabel.pack(side=BOTTOM, fill=BOTH, anchor=SW)

        self.chooseFileBtn = Button(controlBtnsFrame, text="Choose Image File", command=self.chooseFile)
        self.chooseFileBtn.pack(side=LEFT)

        self.processImageBtn = Button(controlBtnsFrame, text="Process", justify=LEFT, relief=RAISED,
                                      command=self.processFile)
        self.processImageBtn.pack(side=LEFT, fill=BOTH)

        self.renderImageBtn = Button(controlBtnsFrame, text="Render", justify=LEFT, relief=RAISED,
                                     command=self.renderFile)
        self.renderImageBtn.pack(side=LEFT, fill=BOTH)

        self.robotDrawBtn = Button(controlBtnsFrame, text="Send to Robot", justify=LEFT, relief=RAISED,
                                   command=self.sendToRobot)
        self.robotDrawBtn.pack(side=LEFT, fill=BOTH)

        self.robotPauseBtn = Button(controlBtnsFrame, text="Pause", justify=LEFT, relief=RAISED,
                                    command=self.pauseDrawing)
        self.robotPauseBtn.pack(side=LEFT, fill=BOTH)

        self.robotResumeBtn = Button(controlBtnsFrame, text="Resume", justify=LEFT, relief=RAISED,
                                     command=self.resumeDrawing)
        self.robotResumeBtn.pack(side=LEFT, fill=BOTH)

        self.setButtonsOff()

        self.progFrame = Frame(master)
        self.progBar = ttk.Progressbar(self.progFrame, maximum=100.1)

        self.timeLabelVar = StringVar()
        self.timeLabelVar.set("00:00:00 / 00:00:00")
        self.timeLabel = Label(self.progFrame, textvariable=self.timeLabelVar, justify=LEFT)

        self.progFrame.pack(side=BOTTOM, fill=BOTH, anchor=SW)
        self.progBar.pack(side=LEFT, fill=BOTH, expand=True, anchor=SW)
        self.timeLabel.pack(side=BOTTOM, anchor=E)

        nbFrame = Frame(master)
        nbFrame.pack(side=TOP, fill=BOTH, expand=1)

        self.nb = notebook(nbFrame, TOP)

        # mkbitmap options
        self.mbOptsGroup = LabelFrame(self.nb, text="mkbitmap options", padx=5, pady=5)
        # self.mbOptsGroup.pack(padx=10, pady=10, side=TOP)

        # wintopo options
        self.wtOptsGroup = LabelFrame(self.nb, text="WinTopo options", padx=5, pady=5)
        # self.wtOptsGroup.pack(padx=10, pady=10, side=TOP)

        # general options
        self.genOptsGroup = LabelFrame(self.nb, text="General options", padx=5, pady=5)

        # put tabs into notebook
        self.nb.add_screen(self.mbOptsGroup, "SVG")
        wintB = self.nb.add_screen(self.wtOptsGroup, "WinTopo")
        self.nb.add_screen(self.genOptsGroup, "Options")

        self.nb.choice.set(1)
        wintB.invoke()

        ###########################
        # svg options

        # filter
        filtFrame = Frame(self.mbOptsGroup)
        filtFrame.pack(side=TOP, anchor=W)

        self.filterVar = IntVar()
        self.filtChk = Checkbutton(filtFrame, text="Filter",
                                   variable=self.filterVar, command=self.filterCb)
        self.filterVar.set(1)
        self.filtChk.pack(side=LEFT)

        self.filtValVar = StringVar()
        self.filtValEnt = Entry(filtFrame, textvariable=self.filtValVar)
        self.filtValVar.set(4)
        self.filtValEnt.pack(side=LEFT)

        # blur
        blurFrame = Frame(self.mbOptsGroup)
        blurFrame.pack(side=TOP, anchor=W)

        self.blurVar = IntVar()
        self.blurChk = Checkbutton(blurFrame, text="Blur",
                                   variable=self.blurVar, command=self.blurCb)
        self.blurChk.pack(side=LEFT, anchor=W)

        self.blurValVar = StringVar()
        self.blurValEnt = Entry(blurFrame, textvariable=self.blurValVar)
        self.blurValEnt['state'] = DISABLED
        self.blurValVar.set(0)
        self.blurValEnt.pack(side=LEFT)

        # scale
        scaleFrame = Frame(self.mbOptsGroup)
        scaleFrame.pack(side=TOP, anchor=W)

        self.scaleVar = IntVar()
        self.scaleChk = Checkbutton(scaleFrame, text="Scale",
                                    variable=self.scaleVar, command=self.scaleCb)
        self.scaleVar.set(1)
        self.scaleChk.pack(side=LEFT, anchor=W)

        self.scaleValVar = StringVar()
        self.scaleValEnt = Entry(scaleFrame, textvariable=self.scaleValVar)
        self.scaleValEnt['state'] = NORMAL
        self.scaleValVar.set(1)
        self.scaleValEnt.pack(side=LEFT)

        # threshold
        threshFrame = Frame(self.mbOptsGroup)
        threshFrame.pack(side=TOP, anchor=W)

        self.threshVar = IntVar()
        self.threshChk = Checkbutton(threshFrame, text="Threshold",
                                     variable=self.threshVar, command=self.threshCb)
        self.threshChk.pack(side=LEFT, anchor=W)

        self.threshValVar = StringVar()
        self.threshValEnt = Entry(threshFrame, textvariable=self.threshValVar)
        self.threshValEnt['state'] = DISABLED
        self.threshValVar.set(0.45)
        self.threshValEnt.pack(side=LEFT)

        # interpolation
        interpFrame = Frame(self.mbOptsGroup)
        interpFrame.pack(side=TOP, anchor=W)

        self.interpVar = IntVar()
        self.linRad = Radiobutton(interpFrame, text="Linear", variable=self.interpVar, value=1).pack(side=LEFT,
                                                                                                     anchor=W)
        self.cubRad = Radiobutton(interpFrame, text="Cubic", variable=self.interpVar, value=2).pack(side=LEFT, anchor=W)
        self.interpVar.set(1)

        # invert
        invFrame = Frame(self.mbOptsGroup)
        invFrame.pack(side=TOP, anchor=W)

        self.invertVar = IntVar()
        self.invertChk = Checkbutton(invFrame, text="Invert",
                                     variable=self.invertVar)
        self.invertChk.pack(side=LEFT)

        # grey
        self.greyVar = IntVar()
        self.greyChk = Checkbutton(invFrame, text="Grey",
                                   variable=self.greyVar)
        self.greyChk.pack(side=RIGHT, anchor=E)

        ###########################
        # Wintopo options

        # despeckle
        WTdespecFrame = Frame(self.wtOptsGroup)
        WTdespecFrame.pack(side=TOP, anchor=W)

        self.WTdespecVar = IntVar()
        self.WTdespecChk = Checkbutton(WTdespecFrame, text="Despeckle",
                                       variable=self.WTdespecVar, command=self.WTdespecCb)
        self.WTdespecVar.set(1)
        self.WTdespecChk.pack(side=LEFT)

        self.WTdespecValVar = StringVar()
        self.WTdespecValEnt = Entry(WTdespecFrame, textvariable=self.WTdespecValVar)
        self.WTdespecValVar.set(4)
        self.WTdespecValEnt.pack(side=LEFT)

        ###########################
        # General options

        # serial
        serialFrame = Frame(self.genOptsGroup)
        serialFrame.pack(side=TOP, anchor=W)

        self.serialOnVar = IntVar()
        self.serialOnChk = Checkbutton(serialFrame, text="Serial",
                                       variable=self.serialOnVar, command=self.serialCtrlCb)
        self.serialOnVar.set(1)
        self.serialOnChk.pack(side=LEFT)

        self.comValVar = StringVar()
        self.comValEnt = Entry(serialFrame, textvariable=self.comValVar)
        self.comValVar.set("COM15")
        self.comValEnt.pack(side=LEFT, fill=BOTH)

        # pen servo angles
        penAngleFrame = Frame(self.genOptsGroup)
        penAngleFrame.pack(side=TOP, anchor=W)

        self.penUpLabel = Label(penAngleFrame, text="Pen Up Angle: ")
        self.penUpLabel.pack(side=LEFT, fill=BOTH)

        self.penUpValVar = StringVar()
        self.penUpValEnt = Entry(penAngleFrame, textvariable=self.penUpValVar)
        self.penUpValVar.set("102")
        self.penUpValEnt.pack(side=LEFT, fill=BOTH)

        self.penDownLabel = Label(penAngleFrame, text="Pen Down Angle: ")
        self.penDownLabel.pack(side=LEFT, fill=BOTH)

        self.penDownValVar = StringVar()
        self.penDownValEnt = Entry(penAngleFrame, textvariable=self.penDownValVar)
        self.penDownValVar.set("85")
        self.penDownValEnt.pack(side=LEFT, fill=BOTH)

        # draw connecting lines when simulating robot drawing
        self.drawConnectVar = IntVar()
        self.drawConnectChk = Checkbutton(self.genOptsGroup, text="Render Connecting Lines",
                                          variable=self.drawConnectVar)
        self.drawConnectChk.pack(side=TOP, anchor=W)

        ###########################
        # image windows
        imgFrame = Frame(master)
        imgFrame.pack(side=TOP, anchor=W)

        self.origImgWin = Canvas(imgFrame)
        self.procImgWin = Canvas(imgFrame)
        self.origImgWin.pack(side=LEFT, anchor=W)
        self.procImgWin.pack(side=LEFT, anchor=W)






        # svgDbg.initDebug(self.txtWin)

    # thread func
    def processIncoming(self):
        print "processIncoming"
        self.m_master.update_idletasks()

    # potrace options
    def filterCb(self):
        if self.filterVar.get() == 1:
            self.filtValEnt['state'] = NORMAL
        else:
            self.filtValEnt['state'] = DISABLED

    def blurCb(self):
        if self.blurVar.get() == 1:
            self.blurValEnt['state'] = NORMAL
        else:
            self.blurValEnt['state'] = DISABLED

    def scaleCb(self):
        if self.scaleVar.get() == 1:
            self.scaleValEnt['state'] = NORMAL
        else:
            self.scaleValEnt['state'] = DISABLED

    def threshCb(self):
        if self.threshVar.get() == 1:
            self.threshValEnt['state'] = NORMAL
        else:
            self.threshValEnt['state'] = DISABLED




            # wintopo options

    def WTdespecCb(self):
        if self.WTdespecVar.get() == 1:
            self.WTdespecValEnt['state'] = NORMAL
        else:
            self.WTdespecValEnt['state'] = DISABLED

    # general options
    def serialCtrlCb(self):
        if self.serialOnVar.get() == 1:
            self.comValEnt['state'] = NORMAL
        else:
            self.comValEnt['state'] = DISABLED

    def chooseFile(self):
        picFile = tkFileDialog.askopenfilename(title="Open file", filetypes=[("jpg file", ".jpg"), ("png file", ".png"),
                                                                             ("All files", ".*")])
        print "chosen file: ", picFile
        if len(picFile) == 0:
            return
        self.fileLabelVar.set(picFile)

        self.processFile()

    def processFile(self, fileArg=None):
        if fileArg:
            self.fileLabelVar.set(fileArg)

        picFile = self.fileLabelVar.get()

        # take image and turn it into line data
        if self.nb.choice.get() == 0:
            # process as SVG
            imgW, imgH, svgW, svgH, lineData = imageParser.createImageData(picFile, workingDir,
                                                                           self.origImgWin, self.procImgWin,
                                                                           self.scaleVar.get(), self.scaleValEnt.get(),
                                                                           self.interpVar.get(),
                                                                           self.threshVar.get(),
                                                                           self.threshValEnt.get(),
                                                                           self.filterVar.get(), self.filtValEnt.get(),
                                                                           self.invertVar.get())
        else:
            # process as WinTopo

            # take image and turn it into line data
            imgW, imgH, svgW, svgH, lineData = WTimageParser.createImageData(picFile, workingDir,
                                                                             self.origImgWin, self.procImgWin,
                                                                             self.WTdespecVar.get(),
                                                                             self.WTdespecValEnt.get())

        self.m_procImgW = imgW
        self.m_procImgH = imgH
        self.m_procSvgW = svgW
        self.m_procSvgH = svgH
        self.m_lineData = lineData

        print "got back imgw=%d imgh=%d svgw=%d svgh=%d from  createImageData" % (imgW, imgH, svgW, svgH)

        if dumpLineData:
            outf = open(os.path.join(workingDir, "lineData.txt"), "w")
            for l in lineData:
                outf.write(str(l) + "\n")
            outf.close()

    def renderFile(self):
        # take line data and render it
        if not self.m_renderWin:
            self.m_renderWin = ImageRenderer(self.m_procImgW, self.m_procImgH, self.m_procSvgW, self.m_procSvgH)
            self.m_renderWin.createWinAndDrawLineData(self.m_lineData)
        else:
            self.m_renderWin.createWinAndDrawLineData(self.m_lineData)

        comPort = self.comValVar.get()
        serialOn = self.serialOnVar.get()
        penUpVal = self.penUpValEnt.get()
        penDownVal = self.penDownValEnt.get()
        self.m_robot = RobotDriver(self, comPort, serialOn, penUpVal, penDownVal, self.m_procSvgW, self.m_procSvgH,
                                   self.m_lineData)
        totTime = self.m_robot.calculateTimes()
        self.timeLabelVar.set(self.convToTime(0) + " / " + self.convToTime(totTime))

    # for calling when passing file on command line
    def procFile(self, file):
        self.processFile(file)
        self.renderFile

    def sendToRobot(self):
        # reset time and prog bar
        self.progBar.stop()
        self.timeLabelVar.set("00:00:00 / 00:00:00")
        self.m_robotDriveProgress = 0
        comPort = self.comValVar.get()
        serialOn = self.serialOnVar.get()
        penUpVal = self.penUpValEnt.get()
        penDownVal = self.penDownValEnt.get()

        # take line data and pass to robot
        # driveRobot.passLinesToRobot(self, comPort, serialOn, penUpVal, penDownVal, self.m_procSvgW, self.m_procSvgH, self.m_lineData)
        self.m_robot.sendToRobot()

    def pauseDrawing(self):
        self.m_paused = True
        self.setButtonsOn(False)

    def resumeDrawing(self):
        self.m_paused = False
        self.setButtonsOn(True)

    def pauseBtnPushed(self):
        return self.m_paused

        # if robot drawing: set pause enabled, resume disabled

    # if robot stopped: set pause disable, resume enabled
    def setButtonsOn(self, isRobotDrawing):
        if isRobotDrawing:
            self.robotPauseBtn['state'] = NORMAL
            self.robotResumeBtn['state'] = DISABLED
        else:
            self.robotPauseBtn['state'] = DISABLED
            self.robotResumeBtn['state'] = NORMAL

    def setButtonsOff(self):
        self.robotPauseBtn['state'] = DISABLED
        self.robotResumeBtn['state'] = DISABLED


        # convert time in ms into string HH:MM:SS

    def convToTime(self, ms):
        hours, ms = divmod(ms, 3600000)
        minutes, ms = divmod(ms, 60000)
        seconds = ms / 1000
        return "%02i:%02i:%02i" % (hours, minutes, seconds)

    def updateRobotLine(self, lineType, line, lineno, totlines, timePassed, totTime):
        # svgDbg.add("got lineno:"+str(lineno)+ " totlines="+str(totlines))
        self.m_renderWin.updateLine(line, lineno, lineType, self.drawConnectVar.get())

        # update progress bar
        progress = int((lineno / float(totlines)) * 100)
        if progress > self.m_robotDriveProgress:
            self.progBar.step(progress - self.m_robotDriveProgress)
            self.m_robotDriveProgress = progress

        # update time progress
        self.timeLabelVar.set(self.convToTime(timePassed) + " / " + self.convToTime(totTime))

        return self.m_paused


root = Tk()
app = CreateSvgApp(root)

# default to loading command line arg if specified
if len(sys.argv) > 1:
    root.after(500, app.procFile(sys.argv[1]))

root.mainloop()
