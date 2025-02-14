#-*-coding:utf8;-*-
#qpy:2
#qpy:console
"""
quietTimer.py
James Watson, 2016 March
A ringless timer for x minutes
"""
#import plyer
import time
import androidhelper
droid = androidhelper.Android()

def vib():
  """ vibrate for 1 second """
  droid.vibrate(1000) 

def end_ring():
  for i in range(3):
    time.sleep(2)
    vib()
# https://docs.python.org/2/library/time.html#time.sleep

mins = int(raw_input('Minutes to run: '))
# https://docs.python.org/2/library/functions.html#raw_input
print("Will run for " + str(mins) + " minutes.")

for j in range(mins):
  print"Minute " , j+1
  time.sleep(60)
  droid.makeToast("Minute " + str(j+1) + " end");

print("Time End")
end_ring()
