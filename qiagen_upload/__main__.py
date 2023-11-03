"""
Entrypoint for qiagen_upload
"""
import os
import shutil
import argparse
from . import qiagen_upload


def is_valid_file(parser: argparse.ArgumentParser, arg: str) -> str:
    """
    Check file path is valid
        :param parser (argparse.ArgumentParser):    Holds necessary info to parse cmd
                                                    line into Python data types
        :param arg (str):                           Input argument
    """
    if not os.path.exists(arg):
        parser.error(f"The file {arg} does not exist!")
    else:
        return arg  # Return argument


def arg_parse() -> dict:
    """
    Parse arguments supplied by the command line. Create argument parser, define command
    line arguments, then parse supplied command line arguments using the created
    argument parser
        :return (dict): Parsed command line attributes
    """
    parser = argparse.ArgumentParser(
        description=(
            "Create sample ZIP and XML, generate access token, and upload sample ZIP file to QCII"
            ),
        usage=""
    )
    parser.add_argument(
        "-S",
        "--sample_name",
        type=str,
        help="Sample name string",
        required=True,
    )
    parser.add_argument(
        "-Z",
        "--sample_path",
        type=lambda x: is_valid_file(parser, x),
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
        required=True
    )
    return vars(parser.parse_args())


args = arg_parse()

logfile_path = os.path.join(os.getcwd(), f"{args['sample_name']}.qiagen_upload.log")

create_zip = qiagen_upload.AddXMLtoZIP(args['sample_name'], args['sample_path'])

qiagen_upload.UploadToQiagen(
    args['client_id'], args['client_secret'], args['code_verifier'],
    args['device_code'], create_zip.output_zip, args['sample_name']
    )

shutil.rmtree(create_zip.outdir)
