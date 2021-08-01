#!/bin/bash

oldName=$(git branch --show-current)

git branch -M main
if [[ $oldName == "first" ]]
then
git push heroku_1 main
else
git push heroku_2 main
fi
git branch -M $oldName