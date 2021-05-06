#!/bin/bash

files=$(ls .config | grep .txt)

for file in ${files[@]}
do
if [[ $(echo $file | cut -d "." -f 1) == "key" ]]
then
    key=$(echo $file | cut -d "." -f 1 | tr a-z A-Z)
else
    key=$(echo $file | cut -d "." -f 1 | cut -d "_" -f 2 | tr a-z A-Z)_KEY
fi 
if [[ $(heroku config:set --app $(cat whoami) $key=$(cat .config/$file) $key) ]]
then
echo "Sucess...$key set"
else
echo "Error...$key not set"
fi
done 
