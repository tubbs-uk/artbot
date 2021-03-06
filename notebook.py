from Tkinter import *

class notebook(object):
   def __init__(self, master, side=LEFT):
      self.active_fr = None
      self.count = 0
      self.choice = IntVar(0)
      
      
      # breaks for artbot without these
      self.tk = master.tk
      self._w = master._w
      self.children = master.children
      
      
      
      if side in (TOP, BOTTOM): self.side = LEFT
      else: self.side = TOP
      
      self.rb_fr = Frame(master, borderwidth=2, relief=RIDGE)
      self.rb_fr.pack(side=side, fill=BOTH)
      self.screen_fr = Frame(master, borderwidth=2, relief=RIDGE)
      self.screen_fr.pack(fill=BOTH)
      
   def __call__(self):
      return self.screen_fr
      
   def add_screen(self, fr, title):
      b = Radiobutton(self.rb_fr, text=title, indicatoron=0,
                      variable=self.choice,
                      value=self.count, command=lambda: self.display(fr))
      b.pack(fill=BOTH, side=self.side)
      
      if not self.active_fr:
         fr.pack(fill=BOTH, expand=1, padx=5, pady=5 )
         self.active_fr = fr
      
      self.count += 1
      return b
      
   def display(self, fr):
      self.active_fr.forget()
      fr.pack(fill=BOTH, expand=1, padx=5, pady=5)
      self.active_fr = fr
