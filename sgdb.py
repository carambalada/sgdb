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

import os, sys, MySQLdb
#import ldap
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
def sql_get(db, st, mode):
 cursor = db.cursor()

 try:
  cursor.execute(st)
 except:
  print "Error"

 if mode == "all":
  results = cursor.fetchall()
 if mode == "one":
  results = cursor.fetchone()

 return results
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Assambling a domain name using domain_id
#
def complete_domain(db, domain_id):
 st = "SELECT * FROM domain WHERE id=%d" % domain_id
 row = sql_get(db, st, "one")

 domain_name = row[1]
 parent_id = row[2]

 if parent_id == 0:
  return domain_name
 else:
  return domain_name + '.' + complete_domain(db, parent_id)
  
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Getting domain names
#
# db = db link
# table: table name
# root (bool): include root (first-level) domain names?, i.e. 0 would include "com" in return list
#
def get_domain_names(db, table, root):
 rows = sql_get(db, "SELECT * FROM %s" % table)
 for row in rows:
  print "domain: %s%s" % (row[1], complete_domain(db, table, row[2]))
  
 return 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Getting LDAP credentials
#
def get_ldap_credential(db, credential_id):
 st = "SELECT login,password FROM credential where id=%s" % credential_id
 row = sql_get(db, st, 'one')

 return row
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Getting groups from LDAP
#
def make_basedn(domain_full_name, ou):
 basedn = ou
 levels = domain_full_name.split('.')
 for level in levels:
  #basedn = basedn + ',DC=' + level
  basedn += ',DC=' + level

 return basedn
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Getting groups from LDAP
#
def get_ldap_group_from_ou(domain_full_name, credential, ou):

 ldap_url = "ldap://%s" % domain_full_name
 login = credential[0]
 password = credential[1]

 
 basedn = make_basedn(domain_full_name, ou)

 l = ldap.initialize(ldap_url)

 searchFilter = "(CN=*)"
 searchAttribute = ["cn"]
 #this will scope the entire subtree under UserUnits
 searchScope = ldap.SCOPE_SUBTREE
 #Bind to the server
 try:
  l.protocol_version = ldap.VERSION3
  l.simple_bind_s(login, password) 
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
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Main
#
if len(sys.argv) != 2:
 print 'Please specify one inifile on the command line.'
 sys.exit(1)

dbopt = get_options('db', sys.argv[1])
db = MySQLdb.connect(dbopt['host'],dbopt['user'],dbopt['pass'],dbopt['name'])

st = "SELECT * FROM domain"
rows = sql_get(db, st, 'all')
for row in rows:
 domain_id = row[0]
 parent_id = row[2]
 credential_id = row[3]
 if parent_id != 0:
  domain_full_name = complete_domain(db, domain_id)
  credential = get_ldap_credential(db, credential_id)
  get_ldap_group_from_ou(domain_full_name, credential, "OU=Access groups")

db.close()

