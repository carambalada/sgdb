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
import ConfigParser

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Getting options from ini-file
#
def get_options(section, inifile):
 parser = ConfigParser.SafeConfigParser()
 parser.read(inifile)

 options = {}

 for couple in parser.items(section):
  options[couple[0]] = parser.get(section, couple[0])

 return options
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Getting a row from DB
#
def sql_get_all(db, st):
 cursor = db.cursor()

 try:
  cursor.execute(st)
  results = cursor.fetchall()
 except:
  print "Error"

 return results
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Getting domain tail
#
def get_domin_tail(db, table, domain_id):
 cursor = db.cursor()

 try:
  cursor.execute("SELECT name from %s WHERE id=%d" % (table, domain_id))
  results = cursor.fetchone()
 except:
  print "Error"

 return results
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Getting domain names
#
# db = db link
# table: table name
# root (bool): include root (first-level) domain names?, i.e. 0 would include "com" in return list
#
def get_domain_names(db, table, root):
 rows = sql_get_all(db, "SELECT * FROM %s" % table)
 for row in rows:
  print "domain: %s%s" % (row[1], get_domain_tail(db, table, row[2]))
  
 return 
 

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Main
#
if len(sys.argv) != 2:
 print 'Please specify one inifile on the command line.'
 sys.exit(1)

dbopt = get_options('db', sys.argv[1])
db = MySQLdb.connect(dbopt['host'],dbopt['user'],dbopt['pass'],dbopt['name'])

domains = get_domain_names(db, 'domain', 1)

""" ldap
#for row in dmn:
# print "domain: ", row[0], row[1]

db.close()


l = ldap.initialize('ldap://shops.kl.com')
user = "ldap_query@kl.com"
pw = "1q2w3e4r5t"
basedn = "OU=Access groups,DC=kl,DC=com"
basedn = "OU=Access groups,DC=shops,DC=kl,DC=com"

searchFilter = "(CN=3*)"
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
 print "result: ", result_set[0]
 
except ldap.LDAPError, e:
    print e

l.unbind_s()
"""
