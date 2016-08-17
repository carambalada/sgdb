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

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
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
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Getting a row from DB
#
def fSQLGetRow( db, st ):
 cursor = db.cursor()

 try:
  cursor.execute( st )
  results = cursor.fetchall()
 except:
  print "Error"

 return results
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Main
#
"""
if len(sys.argv) != 2:
 print 'Please specify one inifile on the command line.'
 sys.exit(1)

opt = fGetOptions( sys.argv[1] )
db = MySQLdb.connect(opt['host'],opt['user'],opt['pass'],opt['name'])

dmn = fSQLGetRow( db, "SELECT * FROM dmn" )
print dmn
#for row in dmn:
# print "domain: ", row[0], row[1]

db.close()
"""

""" ldap
"""

l = ldap.initialize('ldap://kl.com')
user = "ldap_query@kl.com"
pw = "1q2w3e4r5t"
basedn = "OU=Users (kl.com),DC=kl,DC=com"

searchFilter = "(CN=Сервис.*)"
searchAttribute = ["postalcode","postofficebox"]
#this will scope the entire subtree under UserUnits
searchScope = ldap.SCOPE_SUBTREE
#Bind to the server
try:
    l.protocol_version = ldap.VERSION3
    l.simple_bind_s(user, pw) 
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
