#!/usr/bin/python
# -*- coding: utf-8 -*-

# A config-file should be passed as a parameter to this script.
# The content of the config-file should be something like this:

# --- Config File ----
# [db]
# host = myhost
# user = myuser
# pass = mypass
# name = myname
# --------------------

import os, sys, MySQLdb, ldap
from ConfigParser import SafeConfigParser

#
# Getting options from ini-file
#
def fGetOptions( inifile ):
 body = file(inifile, 'rt').read()

 parser = SafeConfigParser()
 parser.read(inifile)

 opt = {}
 opt['host'] = parser.get('db','host')
 opt['user'] = parser.get('db','user')
 opt['pass'] = parser.get('db','pass')
 opt['name'] = parser.get('db','name')

 return opt

#
# Main
#
if len(sys.argv) != 2:
 print 'Please specify one inifile on the command line.'
 sys.exit(1)
else:
 opt = fGetOptions( sys.argv[1] )

print opt['host']

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

""" ldap

l = ldap.initialize('ldap://')
binddn = ""
pw = ""
basedn = ""

searchFilter = "(CN=Сервис.*)"
searchAttribute = ["postalcode","postofficebox"]
#this will scope the entire subtree under UserUnits
searchScope = ldap.SCOPE_SUBTREE
#Bind to the server
try:
    l.protocol_version = ldap.VERSION3
    l.simple_bind_s(binddn, pw) 
except ldap.INVALID_CREDENTIALS:
  print "Your username or password is incorrect."
  sys.exit(0)
except ldap.LDAPError, e:
  if type(e.message) == dict and e.message.has_key('desc'):
      print e.message['desc']
  else: 
      print e
  sys.exit(0)

try:    
 ldap_result_id = l.search(basedn, searchScope, searchFilter, searchAttribute, attrsonly=0)
 result_set = []
 while 1:
  result_type, result_data = l.result(ldap_result_id, 0)
  if (result_data == []):
   break
  else:
   if result_type == ldap.RES_SEARCH_ENTRY:
    result_set.append(result_data)
 print "result: ", result_set[0][0][1]['postalCode'][0]
 print "result: ", result_set[0][0][1]['postOfficeBox'][0]
 
except ldap.LDAPError, e:
    print e

l.unbind_s()
"""
