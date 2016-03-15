from Tkinter import *

def initOptions():
    global serialOn
    serialOn = IntVar()
    serialOn.set(0)

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

    global workingDir
    workingDir = "c:/temp/svg_create_tmp"

def getSerialOn():
    return serialOn.get()

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