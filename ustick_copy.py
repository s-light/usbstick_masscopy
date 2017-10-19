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
# import re
import json
import readline

import configdict
from usbstick import USBStick


##########################################

class SystemManager(object):
    """docstring for SystemManager."""

    default_config = {
        'system': {
            'update_interval': 500,
        },
        'source_folder': "",
        'mount_base': "~/ustick_copy/",
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

        if self.verbose:
            print("--> finished.")
            print("config: {}".format(self.config))

    def start_webinterface(arg):
        """Start web interface."""
        pass

    def stop_webinterface(arg):
        """Stop web interface."""
        pass


##########################################

##########################################
def handle_userinput(user_input):
    """Handle userinput in interactive mode."""
    global flag_run
    if user_input == "q":
        flag_run = False
        print("stop script.")
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

    my_systemmanager.start_webinterface()

    if args.interactive:
        # wait for user to hit key.
        flag_run = True
        while flag_run:

            message = (
                "\n" +
                42*'*' + "\n"
                # "  's': stop\n"
                "command: \n"
                # "  'ui': update interval "
                # "'ui:{update_frequency}Hz)'\n"
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
    my_systemmanager.stop_webinterface()

    # if args.interactive:
    #     # as last thing we save the current configuration.
    #     print("\nwrite config.")
    #     my_systemmanager.my_config.write_to_file()

##########################################