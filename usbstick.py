#!/usr/bin/env python3
# coding=utf-8

"""
USB-Stick.

abstraction class for USB-Sticks handling.
needs a pyudev Device Class object as input.
"""

import readline
import subprocess


class USBStick(object):
    """Class providing abstraction of inserted USBStick."""

    def __init__(self, device):
        """Create new USBStick Object."""
        super(USBStick, self).__init__()
        self.device = device
        self.path = self.device.device_path
        self.node = self.device.device_node
        self.label = self.device['ID_FS_LABEL']

    def mount(self):
        """Mount this Stick."""
        pass

    def remove(self):
        """Remove this Stick."""
        pass

    def update_label(self, label):
        """Update the Filesystem Label."""
        pass
        # sudo fatlabel /dev/sda1 MyNewLabel
        command = [
            "fatlabel",
            "{}".format(self.node),
            "{}".format(label),
        ]
        result_string = ""
        try:
            result_string += subprocess.check_output(command).decode()
            # print("result_string", result_string)
        except subprocess.CalledProcessError as e:
            error_message = "failed: {}".format(e)
            print(error_message)
            result_string += error_message
        return result_string

    def copy_files_to_me(self, source_folder):
        """Copy Files from source_folder to this Stick."""
        pass

    def print_properties(self):
        """Print all properties with values for an given device."""
        for prop in self.device.properties:
            print("{}:{}".format(
                prop,
                self.device[prop]
            ))

    def prettyprint(self):
        """Copy Files from source_folder to this Stick."""
        print(
            (
                # 42*'*' + "\n"
                "{}\n"
                "device_node: {}\n"
                "ID_FS_LABEL: {}\n"
            ).format(
                self.device,
                self.device.device_node,
                self.device.properties.get("ID_FS_LABEL")
            )
        )


##########################################
if __name__ == '__main__':

    import pyudev
    context = pyudev.Context()

    usbstick_list = []

    for device in context.list_devices(
        subsystem='block',
        DEVTYPE='partition'
    ):
        if 'ID_BUS' in device:
            if device['ID_BUS'] == 'usb':
                usbstick_list.append(USBStick(device))

    print("Sticks", "-"*42)
    for stick in usbstick_list:
        stick.prettyprint()
    print("X"*42)
