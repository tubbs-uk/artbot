import Tkinter

class SvgDebug:

   def __init__(self):
      #self.dbgWin = dbgWin
      self.debugOn = True

   def add(self, text):
      if not self.debugOn:
         return
      try:
         self.dbgWin.insert('end', text + "\n")
         self.dbgWin.see(Tkinter.END)
      except:
         pass
      print text
      
svgDbg = SvgDebug()
