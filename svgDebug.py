import Tkinter

class SvgDebug:

   def initDebug(self, dbgWin):
      self.dbgWin = dbgWin

   def add(self, text):
      try:
         self.dbgWin.insert('end', text + "\n")
         self.dbgWin.see(Tkinter.END)
      except:
         pass
      print text
      
svgDbg = SvgDebug()
