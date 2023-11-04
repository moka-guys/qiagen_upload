#!/usr/bin/env python3
""" __main__.py

Entrypoint for get_user_code
"""
import sys
import os
import argparse
from . import get_user_code
from logger import Logger
import config
import toolbox


def arg_parse() -> dict:
    """
    Parse arguments supplied by the command line. Create argument parser,
    define command line arguments, then parse supplied command line arguments
    using the created argument parser
        :return (dict): Parsed command line attributes
    """
    info_string = (
        "Generate user code required to register the device "
        "in QCII, and device code and code_verifier required for use "
        "when running the qiagen_upload module"
    )
    try:
        parser = argparse.ArgumentParser(
            description=info_string,
            usage=info_string,
        )
        requirednamed = parser.add_argument_group("Required named arguments")
        requirednamed.add_argument(
            "-CI",
            "--client_id",
            type=str,
            help="Client ID provided by Qiagen",
            required=True,
        )
        return vars(parser.parse_args())
    except Exception as exception:
        logger.exception(
            f"An exception was encountered when parsing command line arguments: {exception}",
        )
        sys.exit(1)


args = arg_parse()
outdir = os.path.join(os.getcwd(), "outputs")
logfile_path = os.path.join(outdir, f"get_user_code_{config.TIMESTAMP}.log")
logger = Logger(logfile_path).logger

if not os.path.isdir(outdir):
    os.mkdir(outdir)

logger.info("Running qiagen_upload %s - get_user_code", toolbox.git_tag())

get_user_code.GetUserCode(args["client_id"], outdir, logger)
