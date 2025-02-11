# http://stackoverflow.com/a/23133992

zf = ZipFile('archive.zip', 'r')
for zi in zf.infolist():
    zf.extract(zi)
    date_time = time.mktime(zi.date_time + (0, 0, -1))
    os.utime(zi.filename, (date_time, date_time))
zf.close()

# http://stackoverflow.com/a/36394938

from os import path, utime
from sys import exit
from time import mktime
from zipfile import ZipFile

def unzip(zipfile, outDirectory):
    dirs = {}

    with ZipFile(zipfile, 'r') as z:
        for f in z.infolist():
            name, date_time = f.filename, f.date_time
            name = path.join(outDirectory, name)
            z.extract(f, outDirectory)

            # still need to adjust the dt o/w item will have the current dt
            date_time = mktime(f.date_time + (0, 0, -1))

            if (path.isdir(name)):
                # changes to dir dt will have no effect right now since files are
                # being created inside of it; hold the dt and apply it later
                dirs[name] = date_time
            else:
                utime(name, (date_time, date_time))

    # done creating files, now update dir dt
    for name in dirs:
       date_time = dirs[name]
       utime(name, (date_time, date_time))

if __name__ == "__main__":

    unzip('archive.zip', 'out')

    exit(0)