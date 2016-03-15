from svgDebug import *
import imageParser
import WTimageParser
import botOptions

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

        # svg import
        self.svgImportGroup = LabelFrame(self.nb, text="SVG Import", padx=5, pady=5)

        # wintopo options
        self.wtOptsGroup = LabelFrame(self.nb, text="WinTopo options", padx=5, pady=5)
        # self.wtOptsGroup.pack(padx=10, pady=10, side=TOP)

        # general options
        self.genOptsGroup = LabelFrame(self.nb, text="General options", padx=5, pady=5)

        # put tabs into notebook
        self.nb.add_screen(self.mbOptsGroup, "Potrace")
        self.nb.add_screen(self.wtOptsGroup, "WinTopo")
        activeTab = self.nb.add_screen(self.svgImportGroup, "SVG Import")
        self.nb.add_screen(self.genOptsGroup, "Options")

        self.nb.choice.set(0)
        activeTab.invoke()

        ###########################
        # potrace options

        # filter
        filtFrame = Frame(self.mbOptsGroup)
        filtFrame.pack(side=TOP, anchor=W)

        self.filtChk = Checkbutton(filtFrame, text="Filter",
                                   variable=botOptions.filterOn, command=self.filterCb)
        self.filtChk.pack(side=LEFT)

        self.filtValEnt = Entry(filtFrame, textvariable=botOptions.filterVal)
        self.filtValEnt.pack(side=LEFT)

        # blur
        blurFrame = Frame(self.mbOptsGroup)
        blurFrame.pack(side=TOP, anchor=W)

        self.blurChk = Checkbutton(blurFrame, text="Blur",
                                   variable=botOptions.blurOn, command=self.blurCb)
        self.blurChk.pack(side=LEFT, anchor=W)

        self.blurValEnt = Entry(blurFrame, textvariable=botOptions.blurVal)
        self.blurValEnt.pack(side=LEFT)

        # scale
        scaleFrame = Frame(self.mbOptsGroup)
        scaleFrame.pack(side=TOP, anchor=W)

        self.scaleChk = Checkbutton(scaleFrame, text="Scale",
                                    variable=botOptions.scaleOn, command=self.scaleCb)
        self.scaleChk.pack(side=LEFT, anchor=W)

        self.scaleValEnt = Entry(scaleFrame, textvariable=botOptions.scaleVal)
        self.scaleValEnt.pack(side=LEFT)

        # threshold
        threshFrame = Frame(self.mbOptsGroup)
        threshFrame.pack(side=TOP, anchor=W)

        self.threshChk = Checkbutton(threshFrame, text="Threshold",
                                     variable=botOptions.threshOn, command=self.threshCb)
        self.threshChk.pack(side=LEFT, anchor=W)

        self.threshValEnt = Entry(threshFrame, textvariable=botOptions.threshVal)
        self.threshValEnt.pack(side=LEFT)

        # interpolation
        interpFrame = Frame(self.mbOptsGroup)
        interpFrame.pack(side=TOP, anchor=W)

        self.linRad = Radiobutton(interpFrame, text="Linear Interpolation", variable=botOptions.interpolationType, value=1).pack(side=LEFT,
                                                                                                     anchor=W)
        self.cubRad = Radiobutton(interpFrame, text="Cubic Interpolation", variable=botOptions.interpolationType, value=2).pack(side=LEFT, anchor=W)

        # invert
        invFrame = Frame(self.mbOptsGroup)
        invFrame.pack(side=TOP, anchor=W)

        self.invertChk = Checkbutton(invFrame, text="Invert",
                                     variable=botOptions.invertOn)
        self.invertChk.pack(side=LEFT)

        ###########################
        # Wintopo options

        # despeckle
        WTdespecFrame = Frame(self.wtOptsGroup)
        WTdespecFrame.pack(side=TOP, anchor=W)

        self.WTdespecChk = Checkbutton(WTdespecFrame, text="Despeckle",
                                       variable=botOptions.WTDespecleOn, command=self.WTdespecCb)
        self.WTdespecChk.pack(side=LEFT)

        self.WTdespecValEnt = Entry(WTdespecFrame, textvariable=botOptions.WTDespecleVal)
        self.WTdespecValEnt.pack(side=LEFT)

        ###########################
        # SVG import

        # choose svg
        chooseSvgFrame = Frame(self.svgImportGroup)
        chooseSvgFrame.pack(side=TOP, anchor=W)

        self.chooseSVGFileBtn = Button(chooseSvgFrame, text="Choose SVG File", command=self.chooseSVGFile)
        self.chooseSVGFileBtn.pack(side=LEFT)

        self.svgFileLabelVar = StringVar()
        self.svgFileLabelVar.set("No file")
        self.svgFileLabel = Label(chooseSvgFrame, textvariable=self.svgFileLabelVar, justify=LEFT)
        self.svgFileLabel.pack(side=BOTTOM, fill=BOTH, anchor=SW)


        ###########################
        # General options

        # serial
        serialFrame = Frame(self.genOptsGroup)
        serialFrame.pack(side=TOP, anchor=W)

        self.serialOnChk = Checkbutton(serialFrame, text="Serial",
                                       variable=botOptions.serialOn, command=self.serialCtrlCb)
        self.serialOnChk.pack(side=LEFT)

        self.comValEnt = Entry(serialFrame, textvariable=botOptions.serialVal)
        self.comValEnt.pack(side=LEFT, fill=BOTH)

        # pen servo angles
        penAngleFrame = Frame(self.genOptsGroup)
        penAngleFrame.pack(side=TOP, anchor=W)

        self.penUpLabel = Label(penAngleFrame, text="Pen Up Angle: ")
        self.penUpLabel.pack(side=LEFT, fill=BOTH)

        self.penUpValEnt = Entry(penAngleFrame, textvariable=botOptions.penUpVal)
        self.penUpValEnt.pack(side=LEFT, fill=BOTH)

        self.penDownLabel = Label(penAngleFrame, text="Pen Down Angle: ")
        self.penDownLabel.pack(side=LEFT, fill=BOTH)

        self.penDownValEnt = Entry(penAngleFrame, textvariable=botOptions.penDownVal)
        self.penDownValEnt.pack(side=LEFT, fill=BOTH)

        # draw connecting lines when simulating robot drawing
        self.drawConnectChk = Checkbutton(self.genOptsGroup, text="Render Connecting Lines",
                                          variable=botOptions.renderConnectingOn)
        self.drawConnectChk.pack(side=TOP, anchor=W)

        ###########################
        # image windows
        imgFrame = Frame(master)
        imgFrame.pack(side=TOP, anchor=W)

        self.origImgWin = Canvas(imgFrame)
        self.procImgWin = Canvas(imgFrame)
        self.origImgWin.pack(side=LEFT, anchor=W)
        self.procImgWin.pack(side=LEFT, anchor=W)


        # get controls to take appropriate enabled/disabled state
        self.serialCtrlCb()
        self.filterCb()
        self.blurCb()
        self.scaleCb()
        self.threshCb()
        self.WTdespecCb()


        # svgDbg.initDebug(self.txtWin)

    # thread func
    def processIncoming(self):
        print "processIncoming"
        self.m_master.update_idletasks()

    # potrace options
    def filterCb(self):
        if botOptions.getFilterOn() == 1:
            self.filtValEnt['state'] = NORMAL
        else:
            self.filtValEnt['state'] = DISABLED

    def blurCb(self):
        if botOptions.getBlurOn() == 1:
            self.blurValEnt['state'] = NORMAL
        else:
            self.blurValEnt['state'] = DISABLED

    def scaleCb(self):
        if botOptions.getScaleOn() == 1:
            self.scaleValEnt['state'] = NORMAL
        else:
            self.scaleValEnt['state'] = DISABLED

    def threshCb(self):
        if botOptions.getThreshOn() == 1:
            self.threshValEnt['state'] = NORMAL
        else:
            self.threshValEnt['state'] = DISABLED




            # wintopo options

    def WTdespecCb(self):
        if botOptions.getWTDespecleOn() == 1:
            self.WTdespecValEnt['state'] = NORMAL
        else:
            self.WTdespecValEnt['state'] = DISABLED

    # general options
    def serialCtrlCb(self):
        if botOptions.getSerialOn() == 1:
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

    def chooseSVGFile(self):
        svgFile = tkFileDialog.askopenfilename(title="Open file", filetypes=[("svg file", ".svg")])
        if len(svgFile) == 0:
            return
        self.svgFileLabelVar.set(svgFile)

        svgW, svgH, lineData = imageParser.convertSvgToLines(svgFile)

        self.m_procImgW = svgW
        self.m_procImgH = svgH
        self.m_procSvgW = svgW
        self.m_procSvgH = svgH
        self.m_lineData = lineData

        self.dumpLineData()


    def processFile(self, fileArg=None):
        if fileArg:
            self.fileLabelVar.set(fileArg)

        picFile = self.fileLabelVar.get()

        # take image and turn it into line data
        if self.nb.choice.get() == 0:
            # process as SVG
            imgW, imgH, svgW, svgH, lineData = imageParser.createImageData(picFile, self.origImgWin, self.procImgWin)
        else:
            # process as WinTopo

            # take image and turn it into line data
            imgW, imgH, svgW, svgH, lineData = WTimageParser.createImageData(picFile, self.origImgWin, self.procImgWin)

        self.m_procImgW = imgW
        self.m_procImgH = imgH
        self.m_procSvgW = svgW
        self.m_procSvgH = svgH
        self.m_lineData = lineData

        print "got back imgw=%d imgh=%d svgw=%d svgh=%d from  createImageData" % (imgW, imgH, svgW, svgH)

        self.dumpLineData()

    def dumpLineData(self):
        if not botOptions.dumpLineData:
            return
        outf = open(os.path.join(botOptions.workingDir, "lineData.txt"), "w")
        for l in self.m_lineData:
            outf.write(str(l) + "\n")
        outf.close()

    def renderFile(self):
        # take line data and render it
        if not self.m_renderWin:
            self.m_renderWin = ImageRenderer(self.m_procImgW, self.m_procImgH, self.m_procSvgW, self.m_procSvgH)
            self.m_renderWin.createWinAndDrawLineData(self.m_lineData)
        else:
            self.m_renderWin.createWinAndDrawLineData(self.m_lineData)

        self.m_robot = RobotDriver(self, self.m_procSvgW, self.m_procSvgH,
                                   self.m_lineData)
        totTime = self.m_robot.calculateTimes()
        self.timeLabelVar.set(self.convToTime(0) + " / " + self.convToTime(totTime))

    # for calling when passing file on command line
    def procFile(self, file):
        self.processFile(file)
        self.renderFile()

    def sendToRobot(self):
        # reset time and prog bar
        self.progBar.stop()
        self.timeLabelVar.set("00:00:00 / 00:00:00")
        self.m_robotDriveProgress = 0

        # take line data and pass to robot
        # driveRobot.passLinesToRobot(self, self.m_procSvgW, self.m_procSvgH, self.m_lineData)
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
        self.m_renderWin.updateLine(line, lineno, lineType)

        # update progress bar
        progress = int((lineno / float(totlines)) * 100)
        if progress > self.m_robotDriveProgress:
            self.progBar.step(progress - self.m_robotDriveProgress)
            self.m_robotDriveProgress = progress

        # update time progress
        self.timeLabelVar.set(self.convToTime(timePassed) + " / " + self.convToTime(totTime))

        return self.m_paused

root = Tk()
# make sure to call this before using any of the bot options
botOptions.initOptions()

if os.path.exists(botOptions.workingDir) == False:
    os.makedirs(botOptions.workingDir)


app = CreateSvgApp(root)

# default to loading command line arg if specified
if len(sys.argv) > 1:
    root.after(500, app.procFile(sys.argv[1]))

root.mainloop()
