import math
# convert rectangular (x, y) to polar (r, a)
# r = sqrt(x*x + y*y), a = atan(y/x)  <- atan = inverse tangent, aka tan-1

def cartesianToPolar(line):
   # convert second point as if relative to 0
   #print "converting line", line
   x = line[2] - line[0]
   y = line[3] - line[1]
   #print "line x = %f y = %f" % (x,y)
   
   try:
      r = math.hypot(x, y)
   except ValueError:
      print "error on sqrt. Couldn't convert", line
      
   try:
      if x == 0.0:
         a = 0.0
      else:
         a = math.degrees(math.atan(y/x))
   except ValueError:
      print "error on atan. Couldn't convert", line
      
   # quadrant II  = a + 180 deg
   # quadrant III = a + 180 deg
   # quadrant IV  = a + 360 deg
   if x < 0.0:
      a += 180.0
   elif y < 0.0:
      a += 360.0

   return [r,a]
   
if __name__ == "__main__":
   # example lines:
   ex1 = [0, 0, 50, 50] # up and to the right (between 0 and 90 degrees)
   ex2 = [0, 0, -50, 50] # up and to the left (between 90 and 180 degrees)
   ex3 = [0, 0, -50, -50] # down and to the left (between 180 and 270 degrees)
   ex4 = [0, 0, 50, -50] # down and to the right (between 270 and 360 degrees)
   ex5 = [984, 4485, 982.0, 4481.0] # real example from linedata

   print cartesianToPolar(ex1)
   print cartesianToPolar(ex2)
   print cartesianToPolar(ex3)
   print cartesianToPolar(ex4)
   print cartesianToPolar(ex5)
