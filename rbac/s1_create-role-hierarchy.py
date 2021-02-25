import argparse
import sys
import re

dbs = [
  'ds_c21',
  'ds_ebs',
  'ds_jde',
  'ds_oc',
  'ds_pm',
  'tf_combined',
]

'''
parser = argparse.ArgumentParser()
parser.add_argument('--dbname', '-d', required=True, choices=dbs)
args = parser.parse_args()

db = args.dbname

databases = [ f'{db}' ]
'''

access_roles = [
  'r_a_{db}_admin'.format(db=d) for d in dbs,
  'r_a_{db}_transformed_rw'.format(db=d) for d in dbs,
  'r_a_{db}_restricted_rw'.format(db=d) for d in dbs,
  'r_a_{db}_transformed_ro'.format(db=d) for d in dbs,
  'r_a_{db}_landed_ro'.format(db=d) for d in dbs,
  ]

function_roles = [
  {
    'name': 'r_f_admin',
    'replace': False,
    'privileges': [
    ],        
    'access_roles': [
      [
        'r_a_{db}_admin'.format(db=d)
        for d in dbs
      ],
    ]
  },
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
        'r_a_{db}_landed_ro'.format(db=d)
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
      [
        'r_a_{db}_transformed_ro'.format(db=d)
        for d in dbs
      ],   
    ]
  },
]


sql = [
  '-- python {}'.format(' '.join(sys.argv)),
  'use role securityadmin;'
]

sql.extend([
  'create role {access_role} if not exists;'.format(access_role=a)
  for a in access_roles
])



sql.extend([
  'grant role {access_role} to role {function_role}; '.format(access_role=p, function_role=f['name'])
  for f in function_roles
  for a in f['access_roles']
  for p in a 
])

sql.extend([
  'grant role {function_role} to role sysadmin;'.format(function_role=f['name'])
  for f in function_roles
])

filename=f'sql/create-role-hierarchy_{db}.sql'
for s in sql:
  with open(filename, 'a') as f:
    print(s, file=f)
