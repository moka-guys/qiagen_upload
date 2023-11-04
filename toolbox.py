#!/usr/bin/env python3
""" toolbox.py

This script contains functions used and imported across multiple modules
"""

import os
import sys
import logging
import subprocess
import json
import argparse


def is_valid_file(parser: argparse.ArgumentParser, arg: str) -> str:
    """
    Check file path is valid
        :param parser (argparse.ArgumentParser):    Holds necessary info to parse cmd
                                                    line into Python data types
        :param arg (str):                           Input argument
        :return (str):                              Input argument
    """
    if not os.path.exists(arg):
        parser.error(f"The file {arg} does not exist!")
    else:
        return arg  # Return argument


def git_tag() -> str:
    """
    Obtain git tag from current commit
        :return stdout (str):   String containing stdout,
                                with newline characters removed
    """
    filepath = os.path.dirname(os.path.realpath(__file__))
    cmd = f"git -C {filepath} describe --tags"

    proc = subprocess.Popen(
        [cmd], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True
    )
    out, _ = proc.communicate()
    if out.decode("utf-8"):
        return out.rstrip().decode("utf-8")
    else:
        return "[unversioned]"


def check_for_error(proc: subprocess.Popen, logger: object) -> (str, str, int):
    """
    Check for success returncode and write to log accordingly
        :param proc (class):    subprocess.Popen class
        :param logger (object): Logger
        :return (stdout(str),
        stderr(str))(tuple):    Stdout, stderr
    """
    out, err = proc.communicate()
    out = json.loads(out.decode("utf-8").strip().splitlines()[-1])
    err = err.decode("utf-8").strip()
    if out.get("error") is None:
        logger.info("Command was executed successfully with no error")
        return out, err
    else:
        logger.info(f"Command failed. Stdout: {out}. Stderr: {err}")
        sys.exit(1)


def execute_subprocess_command(command: str, logger: logging.Logger) -> (str, str, int):
    """
    Execute a subprocess
        :param command(str):            Input command
        :param logger(logging.Logger):  Logger
        :return (stdout(str),
        stderr(str))(tuple):            Outputs from the command
    """
    logger.info(f"Executing command: {command}")
    proc = subprocess.Popen(
        [command],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        shell=True,
        executable="/bin/bash",
    )
    out, err = check_for_error(proc, logger)  # Capture the streams
    return out
