#!/usr/bin/env python3
""" get_user_code.py

Get user_code required to register the device in QCII, and device_code and
code_verifier required for use when running the qiagen_upload module
"""
import sys
import os
import pkce
import config
import logging
import toolbox


class GetUserCode:
    """
    Class to generate the user code, device code and code_verifier for use in
    registering the device in QCII and when running the qiagen_upload module

    Attributes
        client_id (str):            The client for which the code is requested
                                    (provided by QIAGEN)
        logger (object):            Python logging object
        code_verifier (str):        A high-entropy cryptographic random string
        code_challenge (str):       Created by SHA256 hashing the code_verifier
                                    and base64 URL encoding the resulting hash
        device_code_cmd (str):      Command used to generate the user and device
                                    code using the Qiagen API
        user_code (str):            Code for registering device in QiaOAuth
        device_code (str):          Code for authorising the device
        outdir (str):               Directory for output files
        code_verifier_file (str):   File to store code_verifier
        user_code_file (str):       File to store user_code
        device_code_file (str):     File to store device_code

    Methods
        generate_pkce_pair()
            Generate PKCE (Proof Key for Code Exchange) pair
        print_code_verifier()
            Return code_verifier for use in upload_to_qiagen.py
        get_device_code_cmd()
            Construct command used to generate the user and device code using
            the Qiagen API
        generate_device_code()
            Execute the command to generate the user and device code using
            the Qiagen API
        write_code_to_file()
            Write code to output file
    """

    def __init__(self, client_id: str, outdir: str, logger: logging.Logger):
        """
        Constructor for the GetUserCode class
            :param client_id (str):     The client for which the code is requested
                                        (provided by QIAGEN)
            :param outdir (str):        Directory for output files
            :param logger (object):     Python logging object
        """
        self.client_id = client_id
        self.logger = logger
        self.logger.info("Calling GetUserCode class")
        self.code_verifier, self.code_challenge = self.generate_pkce_pair()
        self.device_code_cmd = self.get_device_code_cmd()
        self.user_code, self.device_code = self.generate_device_code()
        self.outdir = outdir
        self.code_verifier_file = os.path.join(
            self.outdir, f"qiagen_code_verifier_{config.TIMESTAMP}.txt"
        )
        self.user_code_file = os.path.join(
            self.outdir, f"qiagen_user_code_{config.TIMESTAMP}.txt"
        )
        self.device_code_file = os.path.join(
            self.outdir, f"qiagen_device_code_{config.TIMESTAMP}.txt"
        )
        self.write_code_to_file(
            self.code_verifier_file, "code_verifier", self.code_verifier
        )
        self.write_code_to_file(self.user_code_file, "user_code", self.user_code)
        self.write_code_to_file(self.device_code_file, "device_code", self.device_code)

    def generate_pkce_pair(self) -> (str, str):
        """
        Generate PKCE (Proof Key for Code Exchange) pair
            :return code_verifier (str):    Code verifier, a high-entropy cryptographic
                                            random string
            :return code_challenge (str):   Code challenge,  created by SHA256 hashing the
                                            code_verifier and base64 URL encoding the resulting hash
        """
        try:
            self.logger.info("Generating code_verifier and code_challenge pkce pair")
            code_verifier, code_challenge = pkce.generate_pkce_pair()
            return code_verifier, code_challenge
        except Exception as exception:
            self.logger.exception(
                "An exception was encountered when generating pkce code_verifier "
                f"and code_challenge pair: {exception}",
            )
            sys.exit(1)

    def get_device_code_cmd(self) -> None:
        """
        Construct command used to generate the user and device code using the Qiagen API
            :return None:
        """
        try:
            self.logger.info("Creating the device code generation command")
            return (
                'curl -i -X POST -H \'Content-Type: application/json\' -d \'{"client_id": "%s", '
                '"code_challenge": "%s", "code_challenge_method": "S256"}\' '
                "'https://apps.qiagenbioinformatics.eu/qiaoauth/oauth/device/code'"
            ) % (self.client_id, self.code_challenge)
        except Exception as exception:
            self.logger.exception(
                "An exception was encountered when creating the device code "
                f"generation command: {exception}",
            )
            sys.exit(1)

    def generate_device_code(self) -> None:
        """
        Execute the command to generate the user and device code using the Qiagen API
            :return None:
        """
        try:
            self.logger.info("Generating device code and user code")
            out = toolbox.execute_subprocess_command(self.device_code_cmd, self.logger)
            self.logger.info(
                "Device code and user code generation command was successful"
            )
            return out["userCode"], out["deviceCode"]
        except Exception as exception:
            self.logger.exception(
                "An exception was encountered when generating the device code "
                f"and user code: {exception}",
            )
            sys.exit(1)

    def write_code_to_file(self, file_path: str, code_type: str, code: str) -> None:
        """
        Write code to output file
            :param file_path (str): Path of file to output the code to
            :param code_type (str): Type of code, for use in log messages
            :param code (str):      Code string, to write to file
        """
        try:
            with open(file_path, "w", encoding="utf-8") as output:
                self.logger.info(f"Writing {code_type} to output file {file_path}")
                output.write(code)
                self.logger.info(f"{code_type} successfully written to output file")
        except Exception as exception:
            self.logger.exception(
                f"An exception was encountered when writing {code_type} "
                f"to output file {file_path}: {exception}",
            )
            sys.exit(1)
