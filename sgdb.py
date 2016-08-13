#!/usr/bin/python

# A config-file should be passed as a parameter to this script.
# The content of the config-file should be something like this:

# --- Config File ----
# [db]
# host = myhost
# user = myuser
# pass = mypass
# name = myname
# --------------------

import sys
import MySQLdb
from ConfigParser import SafeConfigParser

""" ini
if len(sys.argv) != 2:
 print 'Please specify one inifile on the command line.'
 sys.exit(1)

inifile = sys.argv[1]
body = file(inifile, 'rt').read()

parser = SafeConfigParser()
parser.read(inifile)

dbhost = parser.get('db','host')
dbuser = parser.get('db','user')
dbpass = parser.get('db','pass')
dbname = parser.get('db','name')
"""

""" sql
db = MySQLdb.connect("dbhost","dbuser","dbpass","dbname")
cursor = db.cursor()

sql = "select * from employee"

try:
 cursor.execute(sql)
# db.commit()
 results = cursor.fetchall()

 for row in results:
  print "fname = row[0]"
except:
# db.rollback()
 print "Error"

db.close()
"""
