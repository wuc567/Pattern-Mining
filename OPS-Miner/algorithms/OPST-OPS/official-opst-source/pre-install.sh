#! /bin/sh

unzip sdsl-lite.zip
cd sdsl-lite
./install.sh "$(pwd)"/libsdsl
mv libsdsl/ ..




