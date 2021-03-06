#!/bin/sh

setup_git() {
  git config --global user.email "travis@travis-ci.org"
  git config --global user.name "Travis CI"
}

commit_website_files() {
  git checkout master
  git add -f dist # Force is required becuase dist is ignored
  git commit --message "Travis build: $TRAVIS_BUILD_NUMBER [skip ci]"
}

upload_files() {
  git remote add origin-deploy https://${GITHUB_TOKEN}@github.com/NoamDev/hpmor-heb.git > /dev/null 2>&1
  git push --quiet --force --set-upstream origin-deploy master
}

setup_git
commit_website_files
upload_files
