"""
Entrypoint for get_user_code
"""
import argparse
from . import get_user_code


def arg_parse() -> dict:
    """
    Parse arguments supplied by the command line. Create argument parser,
    define command line arguments, then parse supplied command line arguments
    using the created argument parser
        :return (dict): Parsed command line attributes
    """
    parser = argparse.ArgumentParser(
        description=""
    )
    requirednamed = parser.add_argument_group("Required named arguments")
    requirednamed.add_argument(
        "-I",
        "--client_id",
        type=str,
        help="Client ID provided by Qiagen",
        required=True,
    )
    return vars(parser.parse_args())


args = arg_parse()
get_user_code.GetUserCode(args["client_id"])
