#!/bin/sh
source=../home-assistant-core/homeassistant/components/growcube/
dest=custom_components/growcube/
cp ${source}*.py ${dest}
cp ${source}*.json ${dest}
cp -r ${source}/translations ${dest}
