""" get_user_code.py

Get code required to register a device in QiaOAuth
"""
import ast
import json
import pkce
import subprocess


# TODO add logging
class GetUserCode():
    """
    """
    def __init__(self, client_id):
        """
        """
        self.client_id = client_id
        self.code_verifier, self.code_challenge = self.generate_pkce_pair()
        self.print_code_verifier()
        self.device_code_cmd = self.get_device_code_cmd()
        self.user_code, self.device_code = self.generate_device_code()
        self.print_outputs()

    def generate_pkce_pair(self):
        """
        """
        code_verifier, code_challenge = pkce.generate_pkce_pair()
        return code_verifier, code_challenge

    def print_code_verifier(self):
        """
        Return code_verifier for use in upload_to_qiagen.py
        """
        print(f"Code verifier: {self.code_verifier}")

    def get_device_code_cmd(self):
        """
        """
        return (
            "curl -i -X POST -H 'Content-Type: application/json' -d '{\"client_id\": \"%s\", "
            "\"code_challenge\": \"%s\", \"code_challenge_method\": \"S256\"}' "
            "'https://apps.qiagenbioinformatics.eu/qiaoauth/oauth/device/code'") % (self.client_id, self.code_challenge)

    def generate_device_code(self):
        """
        """
        device_code = subprocess.Popen([self.device_code_cmd], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        out, _ = device_code.communicate()
        verification_uri = json.loads(out.decode('utf-8').splitlines()[-1])
        return verification_uri['userCode'], verification_uri['deviceCode']

    def print_outputs(self):
        """
        Return user and device code for use in registering device in QiaOAuth and upload_to_qiagen.py
        """
        print(f"User code: {self.user_code}")
        print(f"Device code: {self.device_code}") 
