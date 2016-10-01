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
# Getting data from the DB
#
def sql_get(st, mode):
 cursor = db.cursor()

 try:
  cursor.execute(st)
 except MySQLdb.Error, e:
  try:
   print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
  except IndexError:
   print "MySQL Error: %s" % str(e)

 if mode == "all":
  results = cursor.fetchall()
 if mode == "one":
  results = cursor.fetchone()

 return results
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Inserting data to the DB
#
def sql_set(st):
 cursor = db.cursor()

 try:
  cursor.execute(st)
 except MySQLdb.Error, e:
  try:
   print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
  except IndexError:
   print "MySQL Error: %s" % str(e)
 
 db.commit()
 lastrowid = cursor.lastrowid

 return lastrowid

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Getting LDAP credentials
#
def get_ldap_credential(credential_id):
 st = 'SELECT login,password FROM credential where id=' + str(credential_id)
 row = sql_get(st, 'one')

 return row
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Getting first CN from a DN
# DN example: CN=3 Extend,OU=internet access [3],OU=Access groups,DC=kl,DC=com
#
def get_cn(dn):
 fromSym = '='
 toSym = ','

 fromNum = dn.find(fromSym) + 1
 toNum = dn.find(toSym)

 dn = dn[fromNum:toNum]

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
# Getting ID of the security group from the DB
#
def get_group_id(group):
 st = 'SELECT id FROM cn where name="' + group + '"'
 value = sql_get(st, 'one')

 if (value):
  value = value[0]
 else:
  st = 'INSERT INTO cn (name) value ("' + group + '")'
  value = sql_set(st)

 return value

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Check wether the principal in the DB or not
#
def check_user(user, group_id):
 st = 'SELECT name FROM principal WHERE name="' + user + '" and group_id=' + str(group_id)
 value = sql_get(st, 'one')

 return value
  
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Main
#
if len(sys.argv) != 2:
 print 'Please specify one inifile on the command line.'
 sys.exit(1)

debug = 2

dbopt = get_options('db', sys.argv[1])
db = MySQLdb.connect(dbopt['host'],dbopt['user'],dbopt['pass'],dbopt['name'])

credential = get_ldap_credential(1)
ldap_bind = {}

st = "SELECT * FROM dn"
rows = sql_get(st, 'all')
attr = 'member'

for row in rows:
 dn_id = row[0]
 dn = row[2]
 group = get_cn(dn)
 group_id = get_group_id(group)
 group_member = get_ldap_obj_prop(dn, attr)

 st = 'UPDATE principal SET dn_id=NULL WHERE dn_id=' + str(dn_id)
 sql_set(st)

 for member in group_member:
  user = get_ldap_obj_prop(member, 'userPrincipalName')
  user = user[0]

  if check_user(user, group_id):
   print 'The principal is found: ' + user
   st = 'UPDATE principal SET dn_id=' + str(dn_id) + ' WHERE name="' + user + '" and group_id=' + str(group_id)
   sql_set(st)

  else:
   print 'The new principal should be inserted: ' + user
   st = 'INSERT INTO principal (group_id,dn_id,name) value (' + str(group_id) + ','+ str(dn_id) + ',"' + user + '")'
   sql_set(st)


 st = 'UPDATE dn SET stamp=NOW() WHERE id=' + str(dn_id)
 sql_set(st)

db.close()
