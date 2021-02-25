#!/bin/bash

if [[ -d deploy ]]; then rm -rf sql; fi
mkdir -p deploy
for file in $(find sql/* -type f -name '*.sql')
do
  dirn=$(dirname $file | sed 's|sql/||')
  vern=$(echo $dirn | sed 's/__.*//')
  path=$(echo $dirn | sed 's|.*__|deploy/|' | sed 's|_|/|g')
  basn=$(basename $file)
  newf=$(echo $basn | sed 's/\./'${vern}'./')
  mkdir -p $path
  echo $path/$newf
  cp $file $path/$newf
done
