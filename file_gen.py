import os, random

for i in range(1,65):
    print "=====",i,"====="
    if i != 32:
        dirStr = "logs_" + str(i)
        if not os.path.exists(dirStr):
            os.mkdir( dirStr )
        print "Created dir",dirStr
        for j in range( random.randrange(5,100) ):
            fName = os.path.join( dirStr , "log_" + str(i) + "_" + str(j) + ".txt" )
            f = file( fName , 'w' )
            print "Created file",fName
            for k in range( random.randrange(1,750) ):
                line = ""
                for l in range( random.randrange(20,141) ):
                    line += chr( random.randrange(32 , 127) )
                line += os.linesep
                f.write( line )
            f.close()