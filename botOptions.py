from Tkinter import *

def initOptions():

    # gui control options
    global filterOn
    filterOn = IntVar()
    filterOn.set(1)

    global filterVal
    filterVal = StringVar()
    filterVal.set(4)

    global blurOn
    blurOn = IntVar()
    blurOn.set(0)

    global blurVal
    blurVal = StringVar()
    blurVal.set(0)

    global scaleOn
    scaleOn = IntVar()
    scaleOn.set(1)

    global scaleVal
    scaleVal = StringVar()
    scaleVal.set(1)

    global threshOn
    threshOn = IntVar()
    threshOn.set(0)

    global threshVal
    threshVal = StringVar()
    threshVal.set(0.45)

    global interpolationType
    interpolationType = IntVar()
    interpolationType.set(1)

    global invertOn
    invertOn = IntVar()
    invertOn.set(0)

    global WTDespecleOn
    WTDespecleOn = IntVar()
    WTDespecleOn.set(1)

    global WTDespecleVal
    WTDespecleVal = StringVar()
    WTDespecleVal.set(4)

    global serialOn
    serialOn = IntVar()
    serialOn.set(0)

    global serialVal
    serialVal = StringVar()
    serialVal.set("COM4")

    global penUpVal
    penUpVal = StringVar()
    penUpVal.set("102")

    global penDownVal
    penDownVal = StringVar()
    penDownVal.set("85")

    global renderConnectingOn
    renderConnectingOn = IntVar()
    renderConnectingOn.set(1)


    # directory and path options
    global workingDir
    workingDir = "c:/temp/svg_create_tmp"

    global potraceDir
    potraceDir = "c:/mikee/tools/potrace-1.13.win64"

    global WTexe
    WTexe = "C:/Program Files (x86)/SoftSoft/WinTopo/Topo.exe"

    # general settings
    global dumpLineData
    dumpLineData = True


def getFilterOn():
    return filterOn.get()

def getFilterVal():
    return filterVal.get()

def getBlurOn():
    return blurOn.get()

def getBlurVal():
    return blurVal.get()

def getScaleOn():
    return scaleOn.get()

def getScaleVal():
    return scaleVal.get()

def getThreshOn():
    return threshOn.get()

def getThreshVal():
    return threshVal.get()

def getInterpolationType():
    return interpolationType.get()

def getInvertOn():
    return invertOn.get()

def getWTDespecleOn():
    return WTDespecleOn.get()

def getWTDespecleVal():
    return WTDespecleVal.get()

def getSerialOn():
    return serialOn.get()

def getSerialVal():
    return serialVal.get()

def getPenUpVal():
    return penUpVal.get()

def getPenDownVal():
    return penDownVal.get()

def getRenderConnectingOn():
    return renderConnectingOn.get()