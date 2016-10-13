#!/usr/bin/env bash

set -e

echo "updating setuptools"
pip install -U setuptools

echo "Installing dependencies"
pip install -r dev-requirements.txt

echo "Downloading and unzipping odm_automation"
wget https://github.com/OpenDevelopmentMekong/odm-automation/archive/master.zip -O /tmp/odm_automation.zip
unzip /tmp/odm_automation.zip -d /tmp/

echo "decrypting private key"
openssl aes-256-cbc -K $encrypted_c70662427194_key -iv $encrypted_c70662427194_iv -in odm_tech_rsa.enc -out ~/.ssh/id_rsa -d

echo "adding to ssh agent"
chmod 600 ~/.ssh/id_rsa
eval `ssh-agent -s`
ssh-add ~/.ssh/id_rsa
