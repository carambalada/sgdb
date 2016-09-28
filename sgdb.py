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
import ldap
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
# Getting LDAP credentials
#
def get_ldap_credential(db, credential_id):
 st = "SELECT login,password FROM credential where id=%s" % credential_id
 row = sql_get(db, st, 'one')

 return row
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Getting first CN from a DN
# ?
#
def get_cn(dn):
 # CN=3 Extend,OU=internet access [3],OU=Access groups,DC=kl,DC=com
 _fromSym = '='
 _toSym = ','

 _from = dn.find(_fromSym) + 1
 _to = dn.find(_toSym)

 dn = dn[_from:_to]

 return dn
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Getting LDAP bind instance
#
def get_ldap_bind(domain):

 if not ldap_bind.has_key(domain):
  url = "ldap://%s" % domain
  login = credential[0]
  password = credential[1]
  ldap_connection = ldap.initialize(url)

  try:
   ldap_connection.protocol_version = ldap.VERSION3
   ldap_connection.simple_bind_s(login, password) 
   ldap_bind[domain] = ldap_connection;

  except ldap.LDAPError, e:
   if type(e.message) == dict and e.message.has_key('desc'):
    print e.message['desc']
   else: 
    print e
   sys.exit(0)

 return ldap_bind[domain]
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Getting LDAP object property
#
def get_ldap_obj_prop(dn, attr):

 domain = get_domain_name_from_dn(dn)
 bind = get_ldap_bind(domain)
 searchScope = ldap.SCOPE_BASE
 searchFilter = "(objectClass=*)"
 # we have to request a list of attribures

 try:    
  ldap_result_id = bind.search(dn, searchScope, searchFilter, [attr], attrsonly=0)
  result_type, result_data = bind.result(ldap_result_id, 0, 10)
 except ldap.LDAPError, e:
  print e

 #
 # result_data[0] is the first element of the list-result. Since search scope is
 # SCOPE_BASE there is only one element in the list.
 # result_data[0] is the DN of the object
 # result_data[1] is a dictionary with keys as in the searched attribute list. 
 # We've got just one key - the searched attribute
 #
 attr_value = result_data[0][1][attr]
 return attr_value

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Getting a domain-name-part from a DN
#
def get_domain_name_from_dn(dn):

 fromSym = 'DC'
 fromNum = dn.find(fromSym)
 string = dn[fromNum:]
 parts = string.split(',')
 fromSym = '='
 string = ''

 for part in parts:
  fromNum = part.find(fromSym) + 1
  if string:
   string += '.' + part[fromNum:]
  else:
   string = part[fromNum:]

 return string

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Main
#
if len(sys.argv) != 2:
 print 'Please specify one inifile on the command line.'
 sys.exit(1)

dbopt = get_options('db', sys.argv[1])
db = MySQLdb.connect(dbopt['host'],dbopt['user'],dbopt['pass'],dbopt['name'])

attr = 'member'
credential = get_ldap_credential(db, 1)
ldap_bind = {}

st = "SELECT * FROM dn"
rows = sql_get(db, st, 'all')
for row in rows:
 dn_id = row[0]
 dn = row[1]
 group_member = get_ldap_obj_prop(dn, attr)
 print dn
 for member in group_member:
  userPrincipalName = get_ldap_obj_prop(member, 'userPrincipalName')
  print userPrincipalName[0]

db.close()
