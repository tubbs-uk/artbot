
import string

from pysvg.parser import *
from pysvg.core import *

svgScale = 10


def convertSvgToLines(svgPath):
    global lineData

    svgDoc = parse(svgPath)

    svgW = int(svgDoc._attributes["width"].split(".")[0])
    svgH = int(svgDoc._attributes["height"].split(".")[0])

    lineData = []
    traverseSvg(svgDoc, svgH)
    #svgDbg.add("finished converting to lines")

    return svgW, svgH, lineData

def addLine(l):
    global lineData
    lineData.append([i/svgScale for i in l])

def convertCubicBezLines(startElemX, startElemY, startX, startY, relX1, relY1, relX2, relY2, relEndX, relEndY):
    pathClosing = False
    startX = int(startX)
    startY = int(startY)
    relX1 = int(relX1)
    relY1 = int(relY1)
    relX2 = int(relX2)
    relY2 = int(relY2)
    relEndX = int(relEndX)
    if relEndY[-1].lower() == 'z':
        relEndY = int(relEndY[0:-1])
        pathClosing = True
    else:
        relEndY = int(relEndY)

    #print("input = startX, startY, relX1, relY1, relX2, relY2, relEndX, relEnd")
    #print(startX, startY, relX1, relY1, relX2, relY2, relEndX, relEndY)

    x1 = startX
    y1 = startY
    x2 = x1 + relX1
    y2 = y1 + relY1
    x3 = x1 + relX2
    y3 = y1 + relY2
    x4 = x1 + relEndX
    y4 = y1 + relEndY

    #print("out = ", x1, y1, x2, y2, x3, y3, x4, y4)


    mid12x = (x1+x2)/2.0
    mid12y = (y1+y2)/2.0
    mid23x = (x2+x3)/2.0
    mid23y = (y2+y3)/2.0
    mid34x = (x3+x4)/2.0
    mid34y = (y3+y4)/2.0

    mid123x = (mid12x+mid23x)/2.0
    mid123y = (mid12y+mid23y)/2.0
    mid234x = (mid23x+mid34x)/2.0
    mid234y = (mid23y+mid34y)/2.0

    # line will go from 1 -> 12 -> 123 -> 234 -> 34 -> 4
    addLine([x1, y1, mid12x, mid12y])
    addLine([mid12x, mid12y, mid123x, mid123y])
    addLine([mid123x, mid123y, mid234x, mid234y])
    addLine([mid234x, mid234y, mid34x, mid34y])
    addLine([mid34x, mid34y, x4, y4])

    if pathClosing:
        addLine([x4, y4, startElemX, startElemY])
        #x4=startElemX
        #y4=startElemY

    return x4, y4, pathClosing

def convertLine(startElemX, startElemY, startX, startY, relX, relY):
    #print("raw input = startX, startY, relX, relY")
    #print(startX, startY, relX, relY)

    pathClosing = False
    startX = int(startX)
    startY = int(startY)
    relX = int(relX)
    if relY[-1].lower() == 'z':
        relY = int(relY[0:-1])
        pathClosing = True
    else:
        relY = int(relY)

    #print("input = startX, startY, relX, relY")
    #print(startX, startY, relX, relY)

    x1 = startX
    y1 = startY
    x2 = x1 + relX
    y2 = y1 + relY

    #print("out = ", x1, y1, x2, y2)

    addLine([x1, y1, x2, y2])

    if pathClosing:
        addLine([x2, y2, startElemX, startElemY])
        x2=startElemX
        y2=startElemY

    return x2, y2, pathClosing

def convertLineAbs(startElemX, startElemY, startX, startY, absX, absY):
    pathClosing = False
    startX = int(startX)
    startY = int(startY)
    relX = int(relX)
    if relY[-1].lower() == 'z':
        relY = int(relY[0:-1])
        pathClosing = True
    else:
        relY = int(relY)

    #print("input = startX, startY, absX, absY")
    #print(startX, startY, absX, absY)

    x1 = startX
    y1 = startY
    x2 = absX
    y2 = absY

    #print("out = ", x1, y1, x2, y2)

    addLine([x1, y1, x2, y2])

    if pathClosing:
        addLine([x2, y2, startElemX, startElemY])
        x2=startElemX
        y2=startElemY

    return x2, y2, pathClosing

def convertPath(pathVal, svgH):
    pathElems = pathVal.split(' ')
    #print "path elems: ", pathElems

    # elem types:
    # M or m - MoveTo
    # C or c - cubic bezier
    # S or s - smooth cubic bezier curve
    # Q or q - quadradic bezier curve
    # T or t - smooth quadradic bezier curve
    # A or a - arc
    # Z or z - close path
    # L or l - line to
    # H or h - horizontal line
    # V or v - vertical line

    currEl = 0
    currX = 0
    currY = 0
    numElems = len(pathElems)

    while currEl != numElems:
        #time.sleep(1)
        elemType = pathElems[currEl][0]
        #print "found elemType ", elemType
        #print "current x = ", currX, " current Y = ", currY

        if elemType == 'M':
            #svgDbg.add("Abs move")
            currX = int(pathElems[currEl][1:])
            currY = int(pathElems[currEl+1])
            startElemX = currX
            startElemY = currY
            currEl += 2
        elif elemType == 'm':
            #svgDbg.add("Rel move")
            currX += int(pathElems[currEl][1:])
            currY += int(pathElems[currEl+1])
            startElemX = currX
            startElemY = currY
            currEl += 2
        elif elemType == 'c':
            #svgDbg.add("Rel cubic bez")
            lastElemType = elemType
            startElemX = currX
            startElemY = currY
            currX, currY, pathClosed = convertCubicBezLines(startElemX, startElemY, currX, currY, pathElems[currEl][1:], pathElems[currEl+1], pathElems[currEl+2], pathElems[currEl+3], pathElems[currEl+4], pathElems[currEl+5])
            if pathClosed:
                startElemX = currX
                startElemY = currY
            #currX, currY = testArgs(pathElems[currEl], pathElems[currEl+1], pathElems[currEl+2], pathElems[currEl+3], pathElems[currEl+4], pathElems[currEl+5])
            currEl += 6
        elif elemType == 'L':
            #svgDbg.add("Abs line")
            lastElemType = elemType
            startElemX = currX
            startElemY = currY
            currX, currY, pathClosed = convertLineAbs(startElemX, startElemY, currX, currY, pathElems[currEl][1:], pathElems[currEl+1])
            startElemX = currX
            startElemY = currY
            currEl += 2
        elif elemType == 'l':
            #svgDbg.add("Rel line")
            lastElemType = elemType
            #startElemX = currX
            #startElemY = currY
            currX, currY, pathClosed = convertLine(startElemX, startElemY, currX, currY, pathElems[currEl][1:], pathElems[currEl+1])
            if pathClosed:
                startElemX = currX
                startElemY = currY
            currEl += 2
        elif elemType == '-' or elemType in string.digits:
            # check if next element is a number, if so is continuation of last element
            if lastElemType.lower() == 'c':
                #svgDbg.add("Continuation of cubic bez")
                #print "adding cubic bez elems", pathElems[currEl], pathElems[currEl+1], pathElems[currEl+2], pathElems[currEl+3], pathElems[currEl+4], pathElems[currEl+5]
                currX, currY, pathClosed = convertCubicBezLines(startElemX, startElemY, currX, currY, pathElems[currEl], pathElems[currEl+1], pathElems[currEl+2], pathElems[currEl+3], pathElems[currEl+4], pathElems[currEl+5])
                startElemX = currX
                startElemY = currY
                currEl += 6
            elif lastElemType == 'L':
                #svgDbg.add("Continuation of abs line")
                currX, currY, pathClosed = convertLineAbs(startElemX, startElemY, currX, currY, pathElems[currEl], pathElems[currEl+1])
                startElemX = currX
                startElemY = currY
                currEl += 2
            elif lastElemType == 'l':
                #svgDbg.add("Continuation of rel line")
                currX, currY, pathClosed = convertLine(startElemX, startElemY, currX, currY, pathElems[currEl], pathElems[currEl+1])
                if pathClosed:
                    startElemX = currX
                    startElemY = currY
                currEl += 2
            else:
                svgDbg.add("unknown continuation %s" % elemType)
                currEl+=1
        else:
            svgDbg.add("unknown elemType %s" % elemType)
            currEl+=1



def traverseSvg(elem, svgH):
    if (isinstance(elem, TextContent)):
        return

    if elem._elementName == "path":
        if 'd' in elem._attributes:
            convertPath(elem._attributes['d'], svgH)
            #win.update()
            #time.sleep(3)

    if len(elem._subElements)!=0:
        for subelement in elem._subElements:
            traverseSvg(subelement, svgH)
