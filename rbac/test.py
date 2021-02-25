import argparse
import sys
import re

profiles = {
  'ds_c21': {
    'sizes': ['xsmall','small'], 
    'schemas': ['dbo','doa','emp','erp','exp','staging']
  },
  'ds_ebs': {
    'sizes': ['xsmall','small'], 
    'schemas': ['dbo','doa','emp','erp','exp','staging']
  },
  'ds_jde': {
    'sizes': ['xsmall'], 
    'schemas': ['dbo','doa','emp','erp','exp','staging']
  },
  'ds_oc': {
    'sizes': ['xsmall'], 
    'schemas': ['dbo','doa','emp','erp','exp','staging']
  },
  'ds_pm': {
    'sizes': ['xsmall'], 
    'schemas': ['dbo','doa','emp','erp','exp','staging']
  },
  'group_assurance_dev': {
    'sizes': ['xsmall'], 
    'schemas': ['cleaned','landed','presented','shared']
  },
}

parser = argparse.ArgumentParser()
parser.add_argument('--division', '-d', required=False, choices=profiles.keys())
parser.add_argument('--environment', '-e', default='${env}', choices=['dev','prod'])
parser.add_argument('--no-revoke', action='store_true', default=False)
args = parser.parse_args()

div = args.division
env = args.environment
revoke = not args.no_revoke
print ("revoke" + str(revoke) + "revoke")

databases = [ f'{div}' ]

warehouses = [
  '{database}_{size}_wh'.format(database=d, size=s)
  for d in databases
  for s in profiles[div]['sizes']
]

# print('[%s]' % ', '.join(map(str, warehouses)))

for items in warehouses:
        print(items)