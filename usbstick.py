#!/usr/bin/env python3
# coding=utf-8

"""
USB-Stick.

abstraction class for USB-Sticks handling.
needs a pyudev Device Class object as input.
this could eventually be used for fixing the label-permission problem:
https://unix.stackexchange.com/questions/229987/udev-rule-to-match-any-usb-storage-device
and hopefully someone posts a real solution:
https://unix.stackexchange.com/questions/399010/change-volume-name-without-sudo-root

here is a script that can manage discs with the help of shell commands
https://stackoverflow.com/a/22454071/574981

the documentation to pyudev:
http://pyudev.readthedocs.io/en/latest/guide.html
"""

import os
import shutil
import subprocess
import threading
# import readline

import pyudev

import configdict


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class USBStick(threading.Thread):
    """Class providing abstraction of inserted USBStick."""

    default_config = {
        'source_folder': "~/StickDataToCopy/",
        'mount_base': "~/ustick_copy/",
        'disc_label': "SUN",
        'files_to_remove': [
            'example.file'
        ],
        'auto_run_steps': {
            'format_as_fat32': False,
            'update_label': False,
            'copy_files_to_me': False,
            'remove_all_meta_files': False,
            'remove_files': False,
        },
    }

    def __init__(self, device_path, config, queue=None):
        """Create new USBStick Object."""
        # threading.Thread.__init__(self)
        super(USBStick, self).__init__()
        self.queue = queue

        self.udev_context = pyudev.Context()
        device = pyudev.Devices.from_path(
            self.udev_context,
            device_path
        )
        self.device = device
        self.path = self.device.device_path
        # device_path: /sys/devices/pci0000:00/0000:00:1d.0/usb2/
        # 2-1/2-1.2/2-1.2.2/2-1.2.2.4/2-1.2.2.4:1.0/
        # host7/target7:0:0/7:0:0:0/block/sdc/sdc1
        self.node = self.device.device_node
        # device_node: /dev/sdc1
        self.label = self.device['ID_FS_LABEL']
        self.mount_point = None
        self.config = configdict.merge_deep(self.default_config, config)

        self.usb_port_path = self.get_usb_port_path()
        self.usb_port_name = self.get_usb_port_name()

    # usb port helper
    def get_usb_port(self):
        """Get USB-Port device."""
        return self.device.find_parent('usb')

    def get_usb_port_path(self):
        """Get USB-Port full path."""
        return self.get_usb_port().device_path

    def get_usb_port_id(self):
        """Get USB-Port id."""
        path_full = self.get_usb_port_path()
        # path_full /sys/devices/pci0000:00/0000:00:1d.0/usb2/
        # 2-1/2-1.2/2-1.2.2/2-1.2.2.4/2-1.2.2.4:1.0
        head, tail = os.path.split(path_full)
        # 2-1.2.2.4:1.0
        port_id = tail.replace(':1.0', '')
        # 2-1.2.2.4
        return port_id

    def get_usb_port_name(self):
        """Get USB-Port name."""
        port_id = self.get_usb_port_id()
        # 2-1.2.2.4
        port_name = port_id.replace('.', '_')
        # 2-1_2_2_4
        return port_name

    def get_usb_port_tree(self):
        """Get USB-Port tree."""
        port_id = self.get_usb_port_id()
        # 2-1.2.2.4
        levels = port_id.split('.')
        # tree = {}
        tree = self
        for level in reversed(levels):
            new_level = {}
            new_level[level] = tree
            tree = new_level
        return tree

    # mount
    def _create_mount_point(self):
        """Create mount point for this Stick."""
        # print("create mount point:")
        rel_mount_point = os.path.join(
            self.config['mount_base'],
            self.get_usb_port_name()
        )
        abs_mount_point = os.path.expanduser(rel_mount_point)
        self.mount_point = abs_mount_point
        # print("mount_point:", self.mount_point)

        # check if mount point allready exsists
        # path.exists only works reliable on absolute paths
        if not os.path.exists(self.mount_point):
            # print("create path")
            os.makedirs(self.mount_point)

    def _remove_mount_point(self):
        """Remove mount point for this Stick."""
        if os.path.exists(self.mount_point):
            # print("remove path")
            os.rmdir(self.mount_point)
            self.mount_point = None

    def mount(self):
        """Mount this Stick."""
        self._create_mount_point()
        if self.mount_point:
            # mount
            #   --source /dev/sdc1
            #   --target /home/stefan/ustick_copy/2-1_2_2_4
            # mount needs root / sudo
            command = [
                "mount",
                "--source={}".format(self.node),
                "--target={}".format(self.mount_point),
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

    def unmount(self):
        """Unmount this Stick."""
        if self.mount_point:
            # umount
            #   /dev/sdc1
            #   /home/stefan/ustick_copy/2-1_2_2_4
            # umount needs root / sudo
            command = [
                "umount",
                "{}".format(self.mount_point),
            ]
            result_string = ""
            try:
                result_string += subprocess.check_output(command).decode()
                # print("result_string", result_string)
            except subprocess.CalledProcessError as e:
                error_message = "failed: {}".format(e)
                print(error_message)
                result_string += error_message
            else:
                self._remove_mount_point()
            return result_string
        else:
            print("stick not mounted by this scirpt.")

    # mount with user rights
    def user_mount(self):
        """Mount this stick with user rights."""
        # self._create_mount_point()
        mount_point_label = "usbstick_" + self.get_usb_port_name()
        if mount_point_label:
            # pmount /dev/sdc1 ustick_copy/2-1_2_2_4
            command = [
                "pmount",
                "{}".format(self.node),
                "{}".format(mount_point_label),
            ]
            result_string = ""
            try:
                result_string += subprocess.check_output(command).decode()
                # print("result_string", result_string)
            except subprocess.CalledProcessError as e:
                error_message = "failed: {}".format(e)
                print(error_message)
                result_string += error_message
            else:
                self.mount_point = os.path.join(
                    "/media",
                    mount_point_label
                )
            return result_string

    def user_unmount(self):
        """Unmount this stick with user rights."""
        if self.mount_point:
            # pumount /dev/sdc1
            command = [
                "pumount",
                "{}".format(self.node),
            ]
            result_string = ""
            try:
                result_string += subprocess.check_output(command).decode()
                # print("result_string", result_string)
            except subprocess.CalledProcessError as e:
                error_message = "failed: {}".format(e)
                print(error_message)
                result_string += error_message
            else:
                self.mount_point = None
            return result_string
        else:
            print("stick not mounted by this scirpt.")

    # label things
    def update_label(self, label=None):
        """Update the Filesystem Label."""
        # fatlabel /dev/sda1 MyNewLabel
        if label is None:
            label = self.config['disc_label']
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

    # format
    def format_as_fat32(self, label=None):
        """Format as fat32 and set label."""
        if label is None:
            label = self.config['disc_label']
        # mkfs -t fat -F 32 -n "world" /dev/sdb1
        # mkfs -t fat -F 32 -n "world" /dev/sdb1
        command = [
            "mkfs.fat",
            # "-t=fat",
            "-F 32",
            "-n {}".format(label),
            "{}".format(self.mount_point),
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

    # copy files
    def copy_files_to_me(self, src=None):
        """Copy Files from source_folder to this Stick."""
        # based on
        # https://docs.python.org/3/library/shutil.html#shutil.copy2
        dst = self.mount_point
        if src is None:
            src = self.config['source_folder']
        src_abs = os.path.expanduser(src)
        # first check if device is mounted.
        if os.path.exists(dst):
            self._copy_files(src_abs, dst)
        else:
            print(
                "error: destination '{}' does not exist! "
                "check if Stick is mounted!".format(dst)
            )

    def _copy_files(self, src, dst):
        errors = []
        names = os.listdir(src)
        for name in names:
            self._copy_file(src, dst, name, errors)
        try:
            shutil.copystat(src, dst)
        except OSError as why:
            # can't copy file access times on Windows
            if why.winerror is None:
                errors.extend((src, dst, str(why)))
        if errors:
            raise Error(errors)

    def _copy_file(self, src, dst, name, errors):
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                os.makedirs(dstname)
                self._copy_files(srcname, dstname)
            else:
                shutil.copy2(srcname, dstname)
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as err:
            errors.extend(err.args[0])
        if errors:
            raise Error(errors)

    # remove files
    def remove_all_meta_files(self):
        """Remove all meta files from this Stick."""
        # based on
        # https://docs.python.org/3/library/os.html#os.walk
        meta_files = [
            '.DS_Store'
        ]
        for root, dirs, files in os.walk(self.mount_point, topdown=False):
            for name in files:
                if name in meta_files:
                    full_path = os.path.join(root, name)
                    print("remove: {}".format(full_path))
                    os.remove(full_path)

    def remove_files(self, file_list=None):
        """Remove Files in file_list from this Stick."""
        if file_list is None:
            file_list = self.config['files_to_remove']
        for file_name in file_list:
            full_path = os.path.join(self.mount_point, file_name)
            try:
                os.remove(full_path)
                print("removed: {}".format(full_path))
            except FileNotFoundError as e:
                print(e)

    # helper
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

    def show_port_message(self, message):
        """Show message for a device with port_path."""
        if self.queue:
            # queue_item = (self.port_path, message)
            # print(queue_item)
            # self.queue.put(queue_item)
            self.queue.put((self.usb_port_path, message))
        else:
            print("Port {}: {}".format(
                self.usb_port_name,
                message
            ))

    def _run_mounted(self):
        auto_run_steps = self.config['auto_run_steps']
        # ******************************************
        # real work to do:

        if auto_run_steps['copy_files_to_me']:
            # copy files
            self.show_port_message("copy")
            self.copy_files_to_me()

        if auto_run_steps['remove_all_meta_files']:
            # remove meta files
            self.show_port_message("rm meta")
            self.remove_all_meta_files()

        if auto_run_steps['remove_files']:
            # remove files in rm_files_list
            self.show_port_message("rm files")
            self.remove_files()

        # ******************************************

    # thread runner
    def run(self):
        """Auto perform Stick programming."""
        auto_run_steps = self.config['auto_run_steps']
        self.show_port_message("start")
        try:
            if auto_run_steps['format_as_fat32']:
                # format_as_fat32
                self.show_port_message("fat32")
                self.format_as_fat32()

            if auto_run_steps['update_label']:
                # update label
                self.show_port_message("label")
                self.update_label()
        except Exception as e:
            raise e
        else:
            try:
                # mount
                self.mount()
                # self.user_mount()
            except Exception as e:
                raise e
            else:
                try:
                    self._run_mounted()
                except Exception as e:
                    raise e
                finally:
                    try:
                        # un-mount
                        self.unmount()
                        # self.user_unmount()
                    except Exception as e:
                        raise e
        # done :-)
        # now we have to let the user know
        # print("stick '{}' done".format(self.get_usb_port_id()))
        self.show_port_message("done")


##########################################
if __name__ == '__main__':

    context = pyudev.Context()

    usbstick_list = []

    for device in context.list_devices(
        subsystem='block',
        DEVTYPE='partition'
    ):
        if 'ID_BUS' in device:
            if device['ID_BUS'] == 'usb':
                usbstick_list.append(
                    USBStick(device.device_path, {})
                )

    print("Sticks", "-"*42)
    for stick in usbstick_list:
        stick.prettyprint()
    print("X"*42)

# get device:
# device = pyudev.Devices.from_path(context,
#     '/sys/devices/pci0000:00/0000:00:1d.0/usb2/2-1/2-1.2/2-1.2.2/2-1.2.2.4/'
#     '2-1.2.2.4:1.0/host7/target7:0:0/7:0:0:0/block/sdc/sdc1'
# )
