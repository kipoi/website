#!/bin/bash

[ -f "$HOME/.bashrc" ] && source "$HOME/.bashrc"
[ -f "$HOME/.zshrc" ] && source "$HOME/.zshrc"

env_name=kipoiwebsite
path_to_conda_sh=$(conda info --base)/etc/profile.d/conda.sh
source $path_to_conda_sh

conda activate $env_name
# rm original seminar page
rm ../app/models/templates/models/seminar.html
# create seminar page
cookiecutter . --no-input -f
# move seminar page to app
cp seminar/seminar.html ../app/models/templates/models/
# commit changes and pull
git add ../app/models/templates/models/seminar.html
git add seminar/seminar.html
git add cookiecutter.json
git commit -m "Update seminar page"
git pull --rebase

