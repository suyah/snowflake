import argparse
import sys
import re

profiles = {
  'ds_c21': {
    'schemas': ['dbo','doa','emp','erp','exp','staging']
  },
  'ds_ebs': {
    'schemas': ['dbo','erp','fin','gen','ptp']
  },
  'ds_jde': {
    'schemas': ['dbo','erp','fin','gen','ptp']
  },
  'ds_oc': {
    'schemas': ['con','dbo','erp']
  },
  'ds_pm': {
    'schemas': ['dbo','doa','emp','erp','exp']
  },
  'tf_combined': {
    'schemas': ['dbo','doa','emp','exp','fin','ptp','gen']
  },  
}

parser = argparse.ArgumentParser()
parser.add_argument('--dbname', '-d', required=True, choices=profiles.keys())
parser.add_argument('--no-revoke', action='store_true', default=True)
args = parser.parse_args()

db = args.dbname
revoke = not args.no_revoke

databases = [ f'{db}' ]

schemas = profiles[db]['schemas'] + ['public']

objects = [
  'tables',
  'views',
  'materialized views',
  'stages',
  'file formats',
  'external tables',
  'materialized views',
  'streams',
  'tasks',
  'sequences',
  'functions',
  'procedures',
]
'''
  'pipes',
  'masking policies',
'''
role_chain = [
  { 
    'name': [f'r_a_{db}_admin'],
    'replace': False,
    'grants': [
      [
        'all on database {database}'.format(database=d)
        for d in databases
      ],
      [
        'all on {mode} schemas in database {database}'.format(database=d, mode=m)
        for d in databases
        for m in ['all','future']
      ],
      [
        'all on all {object} in schema {database}.{schema}'.format(database=d, schema=s, object=o)
        for d in databases
        for s in schemas
        for o in objects
      ],
      [
        'all on future {object} in database {database}'.format(database=d, object=o)
        for d in databases
        for o in objects
      ],
    ],
  },
  { 
    'name': [f'r_a_{db}_transformed_rw'],
    'replace': False,
    'grants': [
      [
        'usage on database {database}'.format(database=d)
        for d in databases
      ],
      [
        'usage on schema {database}.{schema}'.format(database=d,schema=s)
        for d in databases
        for s in [e for e in schemas if e not in ('erp', 'staging')]        
      ],      
      [
        'create {object} on schema {database}.{schema}'.format(database=d, schema=s, object=o)
        for d in databases
        for s in [e for e in schemas if e not in ('erp', 'staging')]
        for o in ['table','view','materialized view','materialized view','function','procedure','masking policy']
      ],
    ],
  },
    { 
    'name': [f'r_a_{db}_restricted_rw'],
    'replace': False,
    'grants': [
      [
        'usage on database {database}'.format(database=d)
        for d in databases
      ],
      [
        'usage on schema {database}.{schema}'.format(database=d,schema=s)
        for d in databases
        for s in ['erp','staging'] if s in schemas      
      ],         
      [
        'create {object} on schema {database}.{schema}'.format(database=d, schema=s, object=o)
        for d in databases
        for s in ['erp','staging'] if s in schemas
        for o in ['table','view','materialized view','stage','file format','external table','materialized view','function','procedure','masking policy']
      ],
      [
        f'usage on integration S3_WESC_INT'
      ],
    ],
  },
  { 
    'name': [f'r_a_{db}_transformed_ro'],
    'replace': False,
    'grants': [
      [
        'usage on database {database}'.format(database=d)
        for d in databases
      ],
      [
        'usage on schema {database}.{schema}'.format(database=d, schema=s)
        for d in databases
        for s in [e for e in schemas if e not in ('erp', 'staging')]
      ],
      [
        'select, references on {mode} {object} in schema {database}.{schema}'.format(database=d, schema=s, object=o, mode=m)
        for d in databases
        for s in [e for e in schemas if e not in ('erp', 'staging')]
        for m in ['all','future']
        for o in ['tables','views','materialized views']
      ],
    ],
  },
  { 
    'name': [f'r_a_{db}_landed_ro'],
    'replace': False,
    'grants': [
      [
        'usage on database {database}'.format(database=d)
        for d in databases
      ],
      [
        'usage on schema {database}.{schema}'.format(database=d, schema=s)
        for d in databases
        for s in ['erp'] if s in schemas
      ],
      [
        'select, references on {mode} {object} in schema {database}.{schema}'.format(database=d, schema=s, object=o, mode=m)
        for d in databases
        for s in ['erp'] if s in schemas
        for m in ['all','future']
        for o in ['tables','views','materialized views']
      ],
    ],
  },  
]

sql = [
  '-- python {}'.format(' '.join(sys.argv)),
  'use role securityadmin;'
]


if db.startswith('ds_'): 
  sql.extend([ 
    'create {mode} {name};'.format(name=nm, mode='or replace role' if r['replace'] else 'role if not exists')
    for r in role_chain
    for nm in r['name']
  ])
  sql.extend([f'use role r_a_{db}_admin;'])
  sql.extend([ 
  'create schema {schema} if not exists;'.format(schema=s)
  for d in databases
  for s in schemas
  ])
  sql.extend(['use role securityadmin;'])  
  for r in role_chain:
    sql.extend([
      'grant {privilege} to role {name};'.format(name=nm, privilege=p)
        for sp in r['grants']
        for p in sp
        for nm in r['name']
        ])    
else:
  sql.extend([ 
  'create {mode} {name};'.format(name=nm, mode='or replace role' if r['replace'] else 'role if not exists')
  for r in role_chain
  for nm in [e for e in r['name'] if e not in (f'r_a_{db}_landed_ro',f'r_a_{db}_restricted_rw')]
  ])

  sql.extend([f'use role r_a_{db}_admin;'])
  sql.extend([ 
  'create schema {schema} if not exists;'.format(schema=s)
  for d in databases
  for s in schemas
  ])
  sql.extend(['use role securityadmin;'])  

  for r in role_chain:
    sql.extend([
      'grant {privilege} to role {name};'.format(name=nm, privilege=p)
        for sp in r['grants']
        for p in sp
        for nm in [e for e in r['name'] if e not in (f'r_a_{db}_landed_ro',f'r_a_{db}_restricted_rw')]
        ])  

filename=f'sql/access_roles_{db}.sql'
for s in sql:
  with open(filename, 'a') as f:
    print(s, file=f)
