import argparse

parser = argparse.ArgumentParser()
args = parser.parse_args()

users = [
  { 
    'names': [
      'DEROOIJM@WESFARMERS.COM.AU',
      'MEHTAM@WESFARMERS.COM.AU',	
      'NGUYENM@WESFARMERS.COM.AU',
      'RICHTERY@WESFARMERS.COM.AU',
      'VOLKMANNJ@WESFARMERS.COM.AU',
    ], 
    'roles': ['r_f_kpmg_engineer'] 
  },
  { 
    'names': [
      'BARBERM@WESFARMERS.COM.AU',		
      'DELLAGNELLOD@WESFARMERS.COM.AU',	
      'DILLONH@WESFARMERS.COM.AU',		
      'RAJANIJ@WESFARMERS.COM.AU',
    ], 
    'roles': ['r_f_wesc_engineer'] 
  },
  { 
    'names': [
      'SHUANG@WESFARMERS.COM.AU',	
      'echew@wesfarmers.com.au',		
    ], 
    'roles': ['r_f_admin'] 
  },
]

import sys

sql = [
  '-- python {}'.format(' '.join(sys.argv)),
  'use role securityadmin;'
]

sql.extend([
  'grant role {role} to user {name};'.format(name=n, role=r)
  for u in users
  for n in u['names']
  for r in u['roles']
])

sql.extend([
  'alter user {name} set default_role = {role}; '.format(name=n, role=r)
  for u in users
  for n in u['names']
  for r in u['roles'][:1]
])

filename=f'sql/grant_user_roles.sql'
for s in sql:
  with open(filename, 'a') as f:
    print(s, file=f)