#!/bin/bash
set -eou pipefail

# References:
#  - https://github.com/bioconda/bioconda-utils/blob/master/.circleci/build-docs.sh
#  - https://docs.travis-ci.com/user/encrypting-files
#  - https://gist.github.com/domenic/ec8b0fc8ab45f39403dd

# ----------------------------------------------------------------------------
#
# Repository-specific configuration
#
# ----------------------------------------------------------------------------

# Note that the keypair needs to be specific to repo, so if ORIGIN changes, the
# keypair (docs/key.enc, and the corresponding public key in the setting of the
# repo) need to be updated.
BRANCH="master"
ORIGIN="kipoi.github.io"
GITHUB_USERNAME="kipoi"
KEEP_FOLDER="docs"  # don't overwrite these folders
KEEP_FOLDER2="veff-docs"  # ugly hack of repetition. 
KEEP_FOLDER3="interpret-docs"
KEEP_FOLDER4="kipoiseq"



# DOCHTML is where mkdocs is configured to save the output HTML
DOCHTML=`pwd`/app/build

# tmpdir to which built docs will be copied
STAGING=/tmp/${GITHUB_USERNAME}
STAGING_KEEP=/tmp/${GITHUB_USERNAME}-${KEEP_FOLDER}
STAGING_KEEP2=/tmp/${GITHUB_USERNAME}-${KEEP_FOLDER2}
STAGING_KEEP3=/tmp/${GITHUB_USERNAME}-${KEEP_FOLDER3}
STAGING_KEEP4=/tmp/${GITHUB_USERNAME}-${KEEP_FOLDER4}

# Build docs only if ci-runner is testing this branch:
BUILD_DOCS_FROM_BRANCH="master"

# ----------------------------------------------------------------------------
# END repository-specific configuration
# ----------------------------------------------------------------------------

REPO="git@github.com:${GITHUB_USERNAME}/${ORIGIN}.git"

# clone the branch to tmpdir, clean out contents
rm -rf $STAGING
mkdir -p $STAGING
rm -rf ${STAGING_KEEP}
mkdir -p ${STAGING_KEEP}
rm -rf ${STAGING_KEEP2}
mkdir -p ${STAGING_KEEP2}
rm -rf ${STAGING_KEEP3}
mkdir -p ${STAGING_KEEP3}
rm -rf ${STAGING_KEEP4}
mkdir -p ${STAGING_KEEP4}


SHA=$(git rev-parse --verify HEAD)
git clone $REPO $STAGING
cd $STAGING
git checkout $BRANCH || git checkout --orphan $BRANCH
# backup the folder
cp -r ${KEEP_FOLDER} ${STAGING_KEEP}
# backup the folder
cp -r ${KEEP_FOLDER2} ${STAGING_KEEP2}
# backup the folder
cp -r ${KEEP_FOLDER3} ${STAGING_KEEP3}
# backup the folder
cp -r ${KEEP_FOLDER4} ${STAGING_KEEP4}
# remove the existing target folder
rm -r *

# copy over the main website to tmpdir
cp -r ${DOCHTML}/* $STAGING/
# copy over the docs
cp -r ${STAGING_KEEP}/${KEEP_FOLDER} ${STAGING}/
cp -r ${STAGING_KEEP2}/${KEEP_FOLDER2} ${STAGING}/
cp -r ${STAGING_KEEP3}/${KEEP_FOLDER3} ${STAGING}/
cp -r ${STAGING_KEEP4}/${KEEP_FOLDER4} ${STAGING}/

# add .nojekyll
cd $STAGING
touch .nojekyll
git add .nojekyll

echo '<http://kipoi.org>' > README.md
echo 'kipoi.org' > CNAME

# committing with no changes results in exit 1, so check for that case first.
if git diff --quiet; then
    echo "No changes to push -- exiting cleanly"
    exit 0
fi

# Ignore branch
# if [[ $CIRCLE_BRANCH != master ]]; then
#     echo "Not pushing docs because not on branch '$BUILD_DOCS_FROM_BRANCH'"
#     exit 0
# fi


# Add, commit, and push
echo ".*" >> .gitignore
git config user.name "Circle-CI-website"
git config user.email "${GITHUB_USERNAME}@users.noreply.github.com"
git add -A .
git commit --all -m "Updated docs to commit ${SHA}."
echo "Pushing to $REPO:$BRANCH"
git push $REPO $BRANCH &> /dev/null
