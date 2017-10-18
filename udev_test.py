#!/usr/bin/env python3
# coding=utf-8

"""
pyudev tests.

simple tests for the correct udev matchings.
use with interactive flag:

"""

import time

import pyudev


##########################################

context = pyudev.Context()


device = None

# devices = context.list_devices()
# for device in devices.match_subsystem('block') \
# .match_property('ID_BUS', 'usb'):
#     print("-"*42)
#     print(device)
#     # for prop in device.properties:
#     #     print(prop)
#     print("ID_BUS: ", device.properties.get("ID_BUS"))
#     print("ID_USB_INTERFACES: ", device.properties.get("ID_USB_INTERFACES"))
#     print("ID_SERIAL: ", device.properties.get("ID_SERIAL"))
#     # print("-"*42)


# for device in context.list_devices(
#     # sys_name='usb'
#     # subsystem='usb',
#     # SUBSYSTEMS='usb',
#     # this works:
#     subsystem='block',
#     DEVTYPE='partition'
# ):
#     print(device)

# for dev in devices.match(subsystem='block', DEVTYPE='partition'): print(dev)

print("Version 1", "-"*42)
for dev in context.list_devices(
    subsystem='block'
).match_property("ID_BUS", "usb"):
    print(dev)

print("Version 2", "-"*42)
for dev in context.list_devices(
    subsystem='block',
    ID_BUS="usb"
):
    print(dev)

print("Version 3", "-"*42)
for dev in context.list_devices(
    subsystem='block',
    ID_BUS="usb",
    DEVTYPE='partition'
):
    print(dev)
print("problem is that all properties are matche as OR :-(")


##########################################
print("-"*42)
print("start monitoring for block devices with partition:")
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by('block', device_type="partition")


def print_properties(device):
    """Print all properties with values for an given device."""
    for prop in device.properties:
        print("{}:{}".format(
            prop,
            device[prop]
        ))


# def print_attributes(device):
#     """Print all attributes with values for an given device."""
#     for attr in device.attributes:
#         print("{}:{}".format(
#             attr,
#             device[attr]
#         ))


def log_event(action, device):
    """Print an event."""
    print('background event {0.action}: {0.device_path}'.format(device))
    if 'ID_BUS' in device:
        if device['ID_BUS'] == 'usb':
            print("-"*42)
            # for prop in device.attributes:
            #     print(prop)
            print(
                (
                    42*'*' + "\n"
                    "{}\n"
                    "ID_BUS: {}\n"
                    "device_node: {}\n"
                    "DEVNAME: {}\n"
                    "ID_FS_LABEL: {}\n"
                    "ID_FS_LABEL_ENC: {}\n"
                    "ID_SERIAL: {}\n"
                ).format(
                    device,
                    device.properties.get("ID_BUS"),
                    device.device_node,
                    device.properties.get("DEVNAME"),
                    device.properties.get("ID_FS_LABEL"),
                    device.properties.get("ID_FS_LABEL_ENC"),
                    device.properties.get("ID_SERIAL")
                )
            )
            # print("properties", "-"*42)
            # print_properties(device)
            # print("attributes", "-"*42)
            # print_attributes(device)
            print("-"*42)


observer = pyudev.MonitorObserver(monitor, log_event)
observer.start()

# just wait
flag_run = True
try:
    while flag_run:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nstop script.")
    flag_run = False
