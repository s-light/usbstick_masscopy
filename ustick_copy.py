#!/usr/bin/env python3
# coding=utf-8

"""
USB-Stick mass copy tool.

linux python tool to automatically copy files from an source folder to multiple
USB-Sticks.
"""

import sys
import os
import time
# import array
# import struct
import signal
import argparse
import threading
import queue
import json
import readline
import pyudev

import configdict
from usbstick import USBStick


##########################################

class SystemManager(object):
    """docstring for SystemManager."""

    default_config = {
        'source_folder': "~/StickDataToCopy/",
        'mount_base': "~/ustick_copy/",
        'disc_label': "SOMMER",
        'port_map': {},
    }

    path_script = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, filename, verbose=False):
        """Init SystemManager things."""
        super(SystemManager, self).__init__()

        # check for filename
        if not os.path.exists(filename):
            # print(
            #     "filename does not exists.. "
            #     "so we creating a hopefully valid path"
            # )
            # remember config file name
            config_name = os.path.basename(filename)
            # create path on base of script dir.
            # path_to_config = os.path.join(self.path_script, "config")
            path_to_config = self.path_script
            filename = os.path.join(path_to_config, config_name)

        # read config file:
        self.my_config = configdict.ConfigDict(self.default_config, filename)
        # print("my_config.config: {}".format(self.my_config.config))
        self.config = self.my_config.config
        # print("config: {}".format(self.config))

        self.verbose = verbose
        if self.verbose:
            print("config: {}".format(
                json.dumps(
                    self.config,
                    sort_keys=True,
                    indent=4,
                    separators=(',', ': ')
                )
            ))

        # generate absolute path to config files
        path_to_config = os.path.dirname(filename)
        self.config["path_to_config"] = path_to_config

        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.monitor.filter_by('block', device_type="partition")
        self.observer = pyudev.MonitorObserver(
            self.monitor,
            self._even_partition
        )

        self.port_map = self.config['port_map']

        self.mode = None

        self.stick_dict = {}

        self.queue_devices = queue.Queue()
        self.device_handler_thread = threading.Thread(
            target=self.device_handler
        )

        if self.verbose:
            print("--> finished.")
            print("config: {}".format(self.config))

    # def __del__(self):
    #     """Cleanup SystemManager things."""
    #     super(SystemManager, self).__del__()

    def start(self):
        """Start things."""
        self.device_handler_thread.start()
        self.observer.start()
        print("started system in {} mode".format(self.mode))

    def stop(self):
        """Stop things."""
        self.observer.stop()
        self.queue_devices.put(None)
        if self.device_handler_thread.is_alive():
            self.device_handler_thread.join()
        for device_path, stick in self.stick_dict.items():
            if stick.is_alive():
                stick.join()
        print("stopped system from {} mode".format(self.mode))
        self.mode = None

    def _even_partition(self, action, device):
        """Print partition event."""
        # print('background event {0.action}: {0.device_path}'.format(device))
        if 'ID_BUS' in device:
            if device['ID_BUS'] == 'usb':
                print("-"*42)
                print("event: {} '{}'".format(
                    device.action,
                    device.device_path
                ))
                # device_path
                self.queue_devices.put(
                    (device.action, device.device_path)
                )
                print("-"*42)

    def device_handler(self):
        """Handle Device Events."""
        while True:
            queue_item = self.queue_devices.get()
            if queue_item is None:
                break
            # queue_item is valid so we handle it:
            action, device_path = queue_item
            if action == 'add':

                # default_config = {
                #     'source_folder': "~/StickDataToCopy/",
                #     'mount_base': "~/ustick_copy/",
                #     'disc_label': "NEWLABEL",
                #     'port_map': {},
                # }
                config = {}
                config['disc_label'] = self.config['disc_label']
                config['port_map'] = self.port_map
                new_stick = USBStick(device_path, config)
                self.stick_dict[device_path] = new_stick
                if self.mode == 'copy':
                    new_stick.start()
                elif self.mode == 'mapping':
                    port_path = new_stick.get_usb_port_path()
                    if port_path not in self.port_map:
                        self.port_map[port_path] = len(self.port_map)
                        print("new port: {}".format(self.port_map[port_path]))
                else:
                    print("unknown mode: {}".format(self.mode))
            elif action == 'remove':
                if self.stick_dict[device_path].is_alive():
                    print(
                        "attention we have to wait for a device after remove!"
                        "THIS SHOULD NEVER HAPPEN!!!! "
                        "YOU HAVE UNPLUGGED THE STICK BEFORE IT WAS UNMOUNTED"
                        "device_path: {}".format(device_path)
                    )
                    self.stick_dict[device_path].join()
                del self.stick_dict[device_path]
            self.queue_devices.task_done()

    def start_copy(self):
        """Start automatic copy mode."""
        if self.mode is None:
            self.mode = 'copy'
            self.start()
        else:
            print('system is allready running. stop first.')

    def stop_copy(self):
        """Stop automatic copy mode."""
        self.stop()

    def start_mapping(self):
        """Start mapping mode."""
        if self.mode is None:
            # clean up
            self.port_map = {}
            self.mode = 'mapping'
            self.start()
        else:
            print('system is allready running. stop first.')

    def stop_mapping(self):
        """Stop mapping mode."""
        self.stop()
        print("port_map:")
        for device_path, port_number in self.port_map.items():
            print("{:>3} - {}".format(port_number, device_path))
        print("~"*42)
        # store port mapping in config
        self.config['port_map'] = self.port_map

    def show_stick_status(self, device_path, message):
        """Show message for a device with port_number."""
        port_number = self.port_map[device_path]
        print("Port {}: {}".format(
            port_number,
            message
        ))

##########################################


##########################################
def handle_userinput(user_input):
    """Handle userinput in interactive mode."""
    global flag_run
    if user_input == "q":
        flag_run = False
        print("stop script.")
    elif user_input.startswith("map"):
        my_systemmanager.start_mapping()
    elif user_input.startswith("done"):
        my_systemmanager.stop_mapping()
    elif user_input.startswith("start"):
        my_systemmanager.start()
    elif user_input.startswith("stop"):
        my_systemmanager.stop()
    elif user_input.startswith("source"):
        # try to extract repeate_snake
        start_index = user_input.find(':')
        if start_index > -1:
            source_folder_new = user_input[start_index+1:]
            if os.path.exists(source_folder_new):
                my_systemmanager.config['source_folder'] = (
                    source_folder_new
                )
                print("set source folder to '{}'.".format(
                    my_systemmanager.config['source_folder']
                ))
            else:
                print("input not a valid path.")
    elif user_input.startswith("sc"):
        # try to extract universe value
            print("\nwrite config.")
            my_systemmanager.my_config.write_to_file()


##########################################
if __name__ == '__main__':

    print(42*'*')
    print('Python Version: ' + sys.version)
    print(42*'*')

    ##########################################
    # commandline arguments
    config_default = "./config.json"
    source_default = "~/myfiles"

    parser = argparse.ArgumentParser(
        description="copy source files to multiple USB-Sticks"
    )
    parser.add_argument(
        "-c",
        "--config",
        help="specify a location for the config file (defaults to {})".format(
            config_default
        ),
        metavar='CONFIG',
        default=config_default
    )
    parser.add_argument(
        "-s",
        "--source",
        help="start with given pattern",
        metavar='SOURCE_FOLDER',
        default=source_default
    )
    parser.add_argument(
        "-i",
        "--interactive",
        help="run in interactive mode",
        action="store_true"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="show advanced log information",
        action="store_true"
    )
    args = parser.parse_args()

    ##########################################
    # prepare:
    if args.interactive:
        print(42*'*')
        print(__doc__)
        print(42*'*')

    # init flag_run
    flag_run = False

    # helper
    def _exit_helper(signal, frame):
        """Stop loop."""
        global flag_run
        flag_run = False

    # setup termination and interrupt handling:
    signal.signal(signal.SIGINT, _exit_helper)
    signal.signal(signal.SIGTERM, _exit_helper)

    my_systemmanager = SystemManager(args.config, args.verbose)

    # overwritte with pattern name from comandline
    if "source" in args:
        if args.source != source_default:
            my_systemmanager.config['source_folder'] = args.source

    if args.interactive:
        # wait for user to hit key.
        flag_run = True
        while flag_run:

            message = (
                "\n" +
                42*'*' + "\n"
                "commands: \n"
                "  'map': start mapping mode \n"
                "  'done': stop mapping mode \n"
                "  'start': start copy mode \n"
                "  'stop': stop copy mode \n"
                "  'source': update source folder "
                "'source:~/StickDataToCopy/'\n"
                "  'sc': save config 'sc'\n"
                "Ctrl+C or 'q' to stop script\n" +
                42*'*' + "\n"
                "\n"
            ).format(
                # update_frequency=(
                #     1000.0/my_systemmanager.config['system']['update_interval']
                # ),
            )
            try:
                if sys.version_info.major >= 3:
                    # python3
                    user_input = input(message)
                elif sys.version_info.major == 2:
                    # python2
                    user_input = raw_input(message)
                else:
                    # no input methode found.
                    value = "q"
            except KeyboardInterrupt:
                print("\nstop script.")
                flag_run = False
            except EOFError:
                print("\nstop script.")
                flag_run = False
            except Exception as e:
                print("unknown error: {}".format(e))
                flag_run = False
                print("stop script.")
            else:
                try:
                    if len(user_input) > 0:
                        handle_userinput(user_input)
                except Exception as e:
                    print("unknown error: {}".format(e))
                    flag_run = False
                    print("stop script.")
    # if not interactive
    else:
        # just wait
        flag_run = True
        try:
            while flag_run:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nstop script.")
            flag_run = False

    # blocks untill thread has joined.
    print("stopping all things")
    my_systemmanager.stop()
    print("done. good bye!")

    # if args.interactive:
    #     # as last thing we save the current configuration.
    #     print("\nwrite config.")
    #     my_systemmanager.my_config.write_to_file()

##########################################
