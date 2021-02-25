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
  }
]

dbs = [
  'ds_c21',
  'ds_ebs',
  'ds_jde',
  'ds_oc',
  'ds_pm',
  'tf_combine',
]

roles = [
  {
    'name': 'r_f_kpmg_engineer',
    'replace': False,
    'privileges': [
      [
        'usage, operate on warehouse {warehouse}'.format(warehouse=w)
        for w in ['VWH_TRANSFORM_XSMALL','VWH_TRANSFORM_MEDIUM']
      ],  
    ],
    'access_roles': [   
      [
        'r_a_{db}_transformed_rw'.format(db=d)
        for d in dbs
      ],
      [
        'r_a_{db}_source_ro'.format(db=d)
        for d in dbs
      ],      
    ]
  },
  {
    'name': 'r_f_wesc_engineer',
    'replace': False,
    'privileges': [
      [
        'usage, operate on warehouse {warehouse}'.format(warehouse=w)
        for w in ['VWH_ETL_XSMALL','VWH_ETL_SMALL']
      ],  
    ],
    'access_roles' :[               
      [
        'r_a_{db}_restricted_rw'.format(db=d)
        for d in dbs
      ], 
    ]
  },
]

import sys

sql = [
  '-- python {}'.format(' '.join(sys.argv)),
  'use role securityadmin;'
]

sql.extend([
  'create {replace} {name}; '.format(name=r['name'], replace='or replace role' if r['replace'] else 'role if not exists')
  for r in roles
])

sql.extend([
  'grant {privilege} to role {name}; '.format(privilege=p, name=r['name'])
  for r in roles
  for ps in r['privileges']
  for p in ps
])

sql.extend([
  'grant role {access_role} to role {name}; '.format(access_role=p, name=r['name'])
  for r in roles
  for a in r['access_roles']
  for p in a
])

sql.extend([
  'grant role {name} to role sysadmin;'.format(name=r['name'])
  for r in roles
])

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

filename=f'sql/function_roles_users.sql'
for s in sql:
  with open(filename, 'a') as f:
    print(s, file=f)