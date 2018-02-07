#!/bin/bash

set -e

FILE_NAME="deploy.zip"

LATEST_RELEASE=$(wget -qO- --header "Accept: application/json" https://github.com/steffeydev/lwasp/releases/latest)
LATEST_VERSION=$(echo $LATEST_RELEASE | sed -e 's/.*"tag_name":"\([^"]*\)".*/\1/')
ARTIFACT_URL="https://github.com/steffeydev/lwasp/releases/download/$LATEST_VERSION/$FILE_NAME"

wget $ARTIFACT_URL
unzip $FILE_NAME
rm $FILE_NAME
cd deploy
./setup
