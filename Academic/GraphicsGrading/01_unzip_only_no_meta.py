import os, shutil

zipFiles = [item for item in os.listdir() if '.zip' in str(item).lower()]

for zf in zipFiles:
    dName = zf.split('/')[-1].split('.')[0].upper()
    os.makedirs( dName, exist_ok = True )
    shutil.unpack_archive( zf, dName )