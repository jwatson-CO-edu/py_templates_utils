#-*-coding:utf8;-*-
#qpy:2
#qpy:console

import random
random.jumpahead(100)
lst = 0
curRun = 0
longrun = 0
count1 = 0
count2 = 0
count3 = 0
for i in range(1000):
  nxt = random.randrange(1,4)
  print nxt,
  if nxt == lst:
    curRun += 1
    if curRun > longrun:
      longrun = curRun
  else:
    curRun = 0
  if nxt == 1:
    count1 += 1
  elif nxt == 2:
    count2 += 1
  elif nxt == 3:
    count3 += 1
  lst = nxt

print
print "1s", count1
print "2s", count2
print "3s", count3
print "Longest Run", longrun
print "Run P", 0.33 ** longrun