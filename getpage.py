
# getpage.py
# James Watson
# 3-07

# This is a script that grabs the html from a website.
# Taken from the "Python Cookbook"

from urllib import urlopen
address = "http://www.python.org"
doc = urlopen(address).read()
print doc

# Instead of 'read' you may also use 'readlines'
