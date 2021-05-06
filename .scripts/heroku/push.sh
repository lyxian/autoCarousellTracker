#!/bin/bash

oldName=$(git branch --show-current)

git branch -M main
git push heroku main
git branch -M $oldName