#!/usr/bin/env python3
# coding=utf-8

"""
just test if permissions are possible to change.

see
https://unix.stackexchange.com/questions/399010/change-volume-name-without-sudo-root
for more information.

first set file permissions:
`sudo setcap CAP_SYS_ADMIN+ep ./format_test.py`

more information at
https://linux.die.net/man/3/cap_from_text

use in interactive mode:
`./permission_test.py`
"""

import subprocess

##########################################
print("-"*42)


def format_device(mount_point=None, label=None):
    """Format device as fat32."""
    if mount_point is None:
        mount_point = "/dev/sdb1"
    if label is None:
        label = "SUN"
    # mkfs -t fat -F 32 -n "world" /dev/sdb1
    command = [
        "mkfs.fat",
        # "-t=fat",
        "-F 32",
        "-n {}".format(label),
        "{}".format(mount_point),
    ]
    print("formating: {}".format(command))
    result_string = ""
    try:
        result_string += subprocess.check_output(command).decode()
        # print("result_string", result_string)
    except subprocess.CalledProcessError as e:
        error_message = "failed: {}".format(e)
        print(error_message)
        result_string += error_message
    return result_string


def update_label(mount_point=None, label=None):
    """Format device as fat32."""
    if mount_point is None:
        mount_point = "/dev/sdb1"
    if label is None:
        label = "SUN"
    # mkfs -t fat -F 32 -n "world" /dev/sdb1
    command = [
        "mkfs.fat",
        # "-t=fat",
        "-F 32",
        "-n {}".format(label),
        "{}".format(mount_point),
    ]
    print("formating: {}".format(command))
    result_string = ""
    try:
        result_string += subprocess.check_output(command).decode()
        # print("result_string", result_string)
    except subprocess.CalledProcessError as e:
        error_message = "failed: {}".format(e)
        print(error_message)
        result_string += error_message
    return result_string


##########################################
message = (
    "do you really want work on /dev/sdb1? \n"
    "-> to format the device with fat32 type 'format' \n"
    "-> to change the label 'label' \n"
)
user_input = input(message)

mount_point = "/dev/sdb1"
label = "Sunny"

if user_input.startswith("format"):
    format_device(mount_point, label)
elif user_input.startswith("label"):
    update_label(mount_point, label)
