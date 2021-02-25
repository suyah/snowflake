import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--no-revoke', action='store_true', default=False)
args = parser.parse_args()

div = 'aac'
env = 'user'
revoke = not args.no_revoke

databases = [ f'{div}_{env}' ]

warehouses = [
  '{database}_{size}_wh'.format(database=d, size=s)
  for d in databases
  for s in ['xsmall']
]

all_schemas = [
  ('public', None)
]

def schemas_per_div(div, schemas=None):
  return [ s for s, d in all_schemas if (d is None or div in d) and (schemas is None or s in schemas) ]

objects = [
  'tables',
  'views',
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

role_chain = [
  { 
    'name': f'{div}_{env}_admin_role',
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
        for s in schemas_per_div(div)
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
    'name': f'{div}_{env}_runner_role',
    'replace': False,
    'grants': [
      [
        'usage, operate on warehouse {warehouse}'.format(warehouse=w)
        for w in warehouses
      ],
      [
        'all on schema {database}.{schema}'.format(database=d, schema=s)
        for d in databases
        for s in schemas_per_div(div)
      ],
      [
        'all on {mode} {object} in schema {database}.{schema}'.format(database=d, schema=s, mode=m, object=o)
        for d in databases
        for s in schemas_per_div(div)
        for m in ['all','future']
        for o in ['tables','views','stages','file formats','external tables','materialized views']
      ],
      [
        'usage on integration wes_aac_{env}_{bucket}_integration'.format(env=e, bucket=b)
        for e in ['dev']
        for b in ['scratch']
      ],
    ],
  },
  { 
    'name': f'{div}_{env}_basic_role',
    'replace': False,
    'grants': [
      [
        'usage on database {database}'.format(database=d)
        for d in databases
      ],
      [
        'usage on schema {database}.{schema}'.format(database=d, schema=s)
        for d in databases
        for s in schemas_per_div(div, ['public'])
      ],
      [
        'select, references on {mode} {object} in schema {database}.{schema}'.format(database=d, schema=s, object=o, mode=m)
        for d in databases
        for s in schemas_per_div(div, ['public'])
        for m in ['all','future']
        for o in ['tables','views']
      ],
    ],
  },
]

import sys, re

sql = [
  '-- python {}'.format(' '.join(sys.argv)),
  'use role securityadmin;'
]

sql.extend([
  'drop role if exists {name};'.format(name=n)
  for n in [f'{div}_{env}_super_role',f'{div}_{env}_restricted_role',f'{div}_{env}_developer_role',f'{div}_{env}_privileged_role']
])

sql.extend([ 
  'create {mode} {name};'.format(name=r['name'], mode='or replace role' if r['replace'] else 'role if not exists')
  for r in role_chain
])

sql.extend([
  'grant role {name} to role {parent};'.format(name=r['name'], parent=p['name'])
  for r, p in zip(role_chain, [{'name':'sysadmin'}] + role_chain)
])

for r in role_chain:
  if revoke and not r['replace']:
    if 'revokes' in r:
      sql.extend([
        'revoke {privilege} from role {name};'.format(name=r['name'], privilege=p)
        for sp in r['revokes']
        for p in sp
      ])
    else:
      sql.extend([
        'revoke {privilege} from role {name};'.format(name=r['name'], privilege=re.sub('^.* on', 'all on', p))
        for sp in r['grants']
        for p in sp
      ])

  sql.extend([
    'grant {privilege} to role {name};'.format(name=r['name'], privilege=p)
    for sp in r['grants']
    for p in sp
  ])

for s in sql:
  print(s)
