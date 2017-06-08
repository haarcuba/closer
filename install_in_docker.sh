#!/bin/bash

name=closer-2.0.1-py3-none-any.whl
packagetime --no-pub --no-git -y
( nc -l 1111 < dist/$name ) &
ssh -l me 172.17.0.2 bash -c "nc 172.17.0.1 1111 > $name ; sudo pip3 install ./$name"
