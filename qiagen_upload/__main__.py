#!/usr/bin/env python3
""" __main__.py

Entrypoint for qiagen_upload
"""
import os
import argparse
from . import qiagen_upload
from logger import Logger
import config
import toolbox


def arg_parse() -> dict:
    """
    Parse arguments supplied by the command line. Create argument parser, define command
    line arguments, then parse supplied command line arguments using the created
    argument parser
        :return (dict): Parsed command line attributes
    """
    info_string = (
        "Create sample ZIP and XML, generate access token, and "
        "upload sample ZIP file to QCII"
    )
    parser = argparse.ArgumentParser(
        description=info_string,
        usage=info_string,
    )
    parser.add_argument(
        "-Z",
        "--sample_path",
        type=lambda x: toolbox.is_valid_file(parser, x),
        help="Zipped folder containing variant files",
        required=True,
    )
    parser.add_argument(
        "-CI",
        "--client_id",
        type=str,
        help="Client ID provided by Qiagen",
        required=True,
    )
    parser.add_argument(
        "-CS",
        "--client_secret",
        type=str,
        help="Client secret provided by Qiagen",
        required=True,
    )
    parser.add_argument(
        "-C",
        "--code_verifier",
        type=str,
        help="Code verifier generated when obtaining the user code",
        required=True,
    )
    parser.add_argument(
        "-D",
        "--device_code",
        type=str,
        help="Device code generated when obtaining the user code",
        required=True,
    )
    return vars(parser.parse_args())


args = arg_parse()
outdir = os.path.join(os.getcwd(), "outputs")
# Extract sample name from sample path
sample_name = args["sample_path"].replace('.zip', '').split("/")[-1]
logfile_path = os.path.join(
    outdir, f"qiagen_upload.{sample_name}.{config.TIMESTAMP}.log"
)
logger = Logger(logfile_path).logger

if not os.path.isdir(outdir):
    os.mkdir(outdir)

logger.info("Running qiagen_upload %s - qiagen_upload", toolbox.git_tag())

create_zip = qiagen_upload.CreateZIP(sample_name, args["sample_path"], logger)

qiagen_upload.UploadToQiagen(
    args["client_id"],
    args["client_secret"],
    args["code_verifier"],
    args["device_code"],
    create_zip.output_zip,
    logger,
)
