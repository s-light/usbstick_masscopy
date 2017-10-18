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
import readline
# import json


##########################################

class SystemManager(object):
    """docstring for SystemManager."""

    def __init__(self, arg):
        """Setup SystemManager."""
        super(SystemManager, self).__init__()
        self.arg = arg


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
    # if "pattern" in args:
    #     my_config.config['system']['pattern_name'] = args.pattern

    my_systemmanager.start()

    if args.interactive:
        # wait for user to hit key.
        flag_run = True
        while flag_run:

            message = (
                "\n" +
                42*'*' + "\n"
                "  's': stop\n"
                # "set option: \n"
                # "  'ui': update interval "
                # "'ui:{update_frequency}Hz)'\n"
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
                        print("TODO: handle userinput")
                        # handle_userinput(user_input)
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
    my_systemmanager.stop()

    # if args.interactive:
    #     # as last thing we save the current configuration.
    #     print("\nwrite config.")
    #     my_systemmanager.my_config.write_to_file()

##########################################
