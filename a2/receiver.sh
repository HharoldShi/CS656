#!/bin/bash

#Run script for sender distributed as part of
#Assignment 2
#Computer Networks (CS 456)
#Number of parameters: 4
#Parameter:
#    $1: <emulator_address>
#    $2: <emulaotr_port>
#    $3: <receiver_port>
#    $4: file_to_write

#For Python implementation
python3 receiver.py $1 $2 $3 "$4"
