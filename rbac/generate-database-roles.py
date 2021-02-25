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
    'name': f'r_a_{db}_transformed_rw',
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
        for o in ['table','view','materialized view','function','procedure']
      ],
    ],
  },
  { 
    'name': f'r_a_{db}_source_rw',
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
        for o in ['table','view','materialized view','stage','file format','external table','function','procedure','masking policy']
      ],
      [
        f'usage on integration S3_WESC_INT'
      ],
    ],
  },
  { 
    'name': f'r_a_{db}_transformed_ro',
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
    'name': f'r_a_{db}_source_ro',
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
    'create {mode} {name};'.format(name=r['name'], mode='or replace role' if r['replace'] else 'role if not exists')
    for r in role_chain
  ])


  for r in role_chain:
    sql.extend([
      'grant {privilege} to role {name};'.format(name=r['name'], privilege=p)
        for sp in r['grants']
        for p in sp
    ])    
else:
  sql.extend([ 
    'create {mode} {name};'.format(name=r['name'], mode='or replace role' if r['replace'] else 'role if not exists')
    for r in role_chain if r['name'] not in (f'r_a_{db}_source_ro',f'r_a_{db}_source_rw')
  ])

  for r in role_chain:
    if r['name'] not in (f'r_a_{db}_source_ro',f'r_a_{db}_source_rw'):
      sql.extend([
        'grant {privilege} to role {name};'.format(name=r['name'], privilege=p)
          for sp in r['grants']
          for p in sp
      ])

 

filename=f'sql/access_roles_{db}.sql'
for s in sql:
  with open(filename, 'a') as f:
    print(s, file=f)
