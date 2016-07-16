from __future__ import print_function
import Tkinter

class SvgDebug:

   def __init__(self):
      #self.dbgWin = dbgWin
      self.debugOn = True

   def add(self, text, noNewline=False):
      if not self.debugOn:
         return
      try:
         self.dbgWin.insert('end', text + "\n")
         self.dbgWin.see(Tkinter.END)
      except:
         pass

      if noNewline:
         print(text, end="")
      else:
         print(text)
      
svgDbg = SvgDebug()
