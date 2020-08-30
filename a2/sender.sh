#!/bin/bash

#Run script for sender distributed as part of
#Assignment 2
#Computer Networks (CS 456)
#Number of parameters: 4
#Parameter:
#    $1: <emulator_address>
#    $2: <emulaotr_port>
#    $3: <sender_port>
#    $4: file_to_read

#For Python implementation
python3 sender.py $1 $2 $3 "$4"
