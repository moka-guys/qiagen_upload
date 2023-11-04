#!/usr/bin/env python3
""" qiagen_upload.py

Upload the zip file containing the XML file to QCII
"""
import sys
import base64
import xml.etree.ElementTree as etree
import os
import shutil
import zipfile
import logging
import toolbox


class CreateZIP:
    """
    Class to add the create the final ZIP file for upload to QCII

    Attributes
        sample_name (str):              Sample name
        sample_zip_folder (str):        Zip folder containing variant files
        logger (object):                Python logging object
        files_to_keep (list):           List of substrings matching the names of
                                        files required in the TSO zip for upload
                                        to QCII
        xml_path (str):                 Path of XML file created by the script
        xml_name (str):                 Name of xml file created by the script
        outdir (str):                   Path to output directory
        outdir_sample_folder (str):     Path to unzipped TSO sample directory
        output_zip (str):               Path to final zip for upload to QCII

    Methods
        extract_zip_contents()
            Extract contents of input sample zip
        write_output_zip()
            Create new output zip file, containing only the files required for upload
            to QCII (files in self. per self.files_to_keep, plus output XML file)
        remove_intermediary_files()
            Remove intermediary files that are not required for the script output
    """

    def __init__(
        self, sample_name: str, sample_zip_folder: str, logger: logging.Logger
    ):
        """
        Constructor for the AddXMLtoZIP class
            :param sample_name (str):          Sample name
            :param sample_zip_folder (str):    Zip folder containing variant files
            :param logger (object):            Python logging object
        """
        self.sample_name = sample_name
        self.sample_zip_folder = sample_zip_folder
        self.logger = logger
        self.logger.info("Calling CreateZIP class")
        self.files_to_keep = [
            "CopyNumberVariants.vcf",
            "CombinedVariantOutput.tsv",
            "MergedSmallVariants.genome.vcf",
        ]
        xml_obj = CreateXML(sample_name, self.logger)
        self.xml_path = xml_obj.xml_outfile
        self.xml_name = xml_obj.xml_name
        self.outdir = os.path.join(os.getcwd(), "outputs")
        self.outdir_sample_folder = os.path.join(self.outdir, self.sample_name)
        self.output_zip = os.path.join(self.outdir, f"{self.sample_name}.zip")
        self.extract_zip_contents()
        self.write_output_zip()
        self.remove_intermediary_files()

    def extract_zip_contents(self) -> None:
        """
        Extract contents of input sample zip
            :return None:
        """
        try:
            self.logger.info("Unzipping the sample zip folder")
            with zipfile.ZipFile(self.sample_zip_folder, mode="r") as archive:
                for file in archive.namelist():
                    archive.extract(file, self.outdir)
        except Exception as exception:
            self.logger.exception(
                f"An exception was encountered when unzipping the sample zip folder: {exception}",
            )
            sys.exit(1)

    def write_output_zip(self) -> None:
        """
        Create new output zip file, containing only the files required for upload
        to QCII (files in self. per self.files_to_keep, plus output XML file)
            :return None:
        """
        try:
            with zipfile.ZipFile(self.output_zip, "w") as zip_ref:
                to_zip = os.listdir(self.outdir_sample_folder)
                for file in to_zip:
                    if any(filename in file for filename in self.files_to_keep):
                        self.logger.info(f"Adding file to zip file for upload: {file}")
                        filepath = os.path.join(self.outdir_sample_folder, file)
                        zip_ref.write(filepath, arcname=file)
                    else:
                        self.logger.info(f"File is not required in TSO upload: {file}")
                zip_ref.write(self.xml_path, arcname=self.xml_name)
        except Exception as exception:
            self.logger.exception(
                f"An exception was encountered when creating the zip folder for upload: {exception}",
            )
            sys.exit(1)

    def remove_intermediary_files(self) -> None:
        """
        Remove intermediary files that are not required for the script output
            :return None:
        """
        try:
            self.logger.info("Removing intermediary xml file")
            os.remove(self.xml_path)
            self.logger.info("Removing intermediary unzipped sample directory")
            shutil.rmtree(self.outdir_sample_folder)
        except Exception as exception:
            self.logger.exception(
                "An exception was encountered when removing intermediary "
                f"files: {exception}"
            )
            sys.exit(1)


class CreateXML:
    """
    Class to create the XML for the QCI sample upload

    Attributes
        sample_name (str):                      Sample name
        logger (object):                        Python logging object
        xml_template (str):                     Path to XML template for QCI sample upload
        combinedvariants_tsv (str):             Path to TSV CombinedVariantOutput file
        copynumbervariants_vcf (str):           Path to VCF CopyNumberVariants file
        mergedvariants_vcf (str):               Path to VCF MergedSmallVariants file
        outdir (str):                           Directory for output files
        xml_name (str):                         Name of xml file created by the script
        xml_outfile (str):                      Path of XML file created by the script
        variants_filenames (list):              List of filenames to be included in the
                                                VariantsFilename subelement within the
                                                VariantsFilenames subelement in the XML file
        xml_root (etree.Element):               XML template data at root level
        sample_element (etree.Element):         XML Sample element
        variantsfilenames_sub (etree.Element):  XML VariantsFilenames element

    Methods
        import_xml_data()
            Import XML data from template file, at root level
        get_xml_element(element_name)
            Extract an XML element from the xml root
        get_sample_subelement()
            Extract a subelement from within the sample element
        add_sample_name()
            Add sample name subelement to Sample element
        add_sample_subjectid()
            Add subject ID subelement to Sample element
        add_variants_filenames()
            Add VariantsFilename subelement to XML for each file that requires upload to
            QCII for the sample
        order_elements()
            Order elements so that they are in alphabetical descending order, as expected by
            the QCII API
        write_to_outfile()
            Write constructed XML to output file
    """

    def __init__(self, sample_name: str, logger: logging.Logger):
        """
        Constructor for the CreateXML class
            :param sample_name (str):   Name of sample for upload
            :param logger (object):     Python logging object
        """
        etree.register_namespace("", "http://qci.qiagen.com/xsd/interpret")
        self.sample_name = sample_name
        self.logger = logger
        self.logger.info("Calling CreateXML class")
        self.xml_template = os.path.join(
            os.getcwd(), "templates", "sample_upload_template.xml"
        )
        self.combinedvariants_tsv = f"{self.sample_name}_CombinedVariantOutput.tsv"
        self.copynumbervariants_vcf = f"{self.sample_name}_CopyNumberVariants.vcf"
        self.mergedvariants_vcf = f"{self.sample_name}_MergedSmallVariants.genome.vcf"
        self.outdir = os.path.join(os.getcwd(), "outputs")
        self.xml_name = f"{self.sample_name}.xml"
        self.xml_outfile = os.path.join(self.outdir, self.xml_name)
        self.variants_filenames = [
            self.combinedvariants_tsv,
            self.copynumbervariants_vcf,
            self.mergedvariants_vcf,
        ]
        self.xml_root = self.import_xml_data()
        self.sample_element = self.get_xml_element("Sample")
        self.variantsfilenames_sub = self.get_sample_subelement("VariantsFilenames")
        self.add_sample_name()
        self.add_sample_subjectid()
        self.add_variants_filenames()
        self.order_elements()
        self.write_to_outfile()

    def import_xml_data(self) -> etree.Element:
        """
        Import XML data from template file, at root level
            :return etree.Element object:   XML template data at root level
        """
        try:
            self.logger.info("Getting XML template root")
            return etree.parse(self.xml_template).getroot()
        except Exception as exception:
            self.logger.exception(
                f"An exception was encountered when getting XML template root: {exception}",
            )
            sys.exit(1)

    def get_xml_element(self, element_name) -> etree.Element:
        """
        Extract an XML element from the xml root
            :param element_name (str):  Name of element to be extracted
            :return (etree.Element):    XML Sample element
        """
        try:
            self.logger.info(f"Finding element {element_name} in XML template root")
            return self.xml_root.find(
                "{http://qci.qiagen.com/xsd/interpret}" + f"{element_name}"
            )
        except Exception as exception:
            self.logger.exception(
                f"An exception was encountered when finding element {element_name} in XML template root: {exception}",
            )
            sys.exit(1)

    def get_sample_subelement(self, subelement) -> etree.Element:
        """
        Extract a subelement from within the sample element
            :param subelement:              Name of subelement within the
                                            XML Sample element
            :return  etree.Element object:  XML VariantsFilenames element
        """
        try:
            self.logger.info(
                f"Finding subelement {subelement} within the XML Sample element"
            )
            return self.sample_element.find(
                "{http://qci.qiagen.com/xsd/interpret}" + f"{subelement}"
            )
        except Exception as exception:
            self.logger.exception(
                f"An exception was encountered when extracting subelement {subelement} "
                f"from within the sample element: {exception}",
            )
            sys.exit(1)

    def add_sample_name(self) -> None:
        """
        Add sample name subelement to Sample element
            :return None:
        """
        try:
            self.logger.info("Adding the sample name subelement to the Sample element")
            name_subelement = etree.SubElement(self.sample_element, "Name")
            name_subelement.text = self.sample_name
        except Exception as exception:
            self.logger.exception(
                "An exception was encountered when adding the sample name "
                f"subelement to the Sample element: {exception}",
            )
            sys.exit(1)

    def add_sample_subjectid(self) -> None:
        """
        Add subject ID subelement to Sample element
            :return None:
        """
        try:
            self.logger.info("Adding subject ID subelement to the Sample element")
            subjectid_subelement = etree.SubElement(self.sample_element, "SubjectId")
            subjectid_subelement.text = self.sample_name
        except Exception as exception:
            self.logger.exception(
                "An exception was encountered when adding the subject ID "
                f"subelement to the Sample element: {exception}"
            )
            sys.exit(1)

    def add_variants_filenames(self) -> None:
        """
        Add VariantsFilename subelement to XML for each file that requires
        upload to QCII for the sample
            :return None:
        """
        try:
            self.logger.info(
                "Adding VariantsFilename subelements to the VariantsFilenames "
                "subelement"
            )
            for filename in self.variants_filenames:
                self.logger.info(f"Adding subelement {filename}")
                VariantsFilename = etree.SubElement(
                    self.variantsfilenames_sub, "VariantsFilename"
                )
                VariantsFilename.text = filename
        except Exception as exception:
            self.logger.exception(
                "An exception was encountered when adding the VariantsFilename "
                f"subelements to the VariantsFilenames subelement: {exception}"
            )
            sys.exit(1)

    def order_elements(self) -> None:
        """
        Order elements so that they are in alphabetical descending order,
        as expected by the QCII API
            :return None:
        """
        try:
            self.logger.info(
                "Sorting the first layer of elements in the XML into "
                "alphabetical descending order"
            )
            self.xml_root[:] = sorted(
                self.xml_root, key=lambda child: (child.tag, child.get("name"))
            )
            self.logger.info(
                "Sorting the second layer of elements in the XML into "
                "alphabetical descending order"
            )
            for c in self.xml_root:
                c[:] = sorted(c, key=lambda child: (child.tag, child.get("desc")))
        except Exception as exception:
            self.logger.exception(
                "An exception was encountered when sorting the "
                f"XML elements: {exception}"
            )
            sys.exit(1)

    def write_to_outfile(self) -> None:
        """
        Write constructed XML to output file
            :return None:
        """
        try:
            self.logger.info(
                f"Writing the constructed XMl to output file {self.xml_outfile}"
            )
            if not os.path.exists(self.outdir):
                self.logger.info(f"Creating output dir: {self.outdir}")
                os.mkdir(self.outdir)
            with open(self.xml_outfile, "w", encoding="utf-8") as output:
                output.write(etree.tostring(self.xml_root).decode())
        except Exception as exception:
            self.logger.exception(
                "An exception was encountered when sorting the "
                f"XML elements: {exception}"
            )
            sys.exit(1)


class UploadToQiagen:
    """
    Class to upload the created zip file to QCII using the API

    Attributes
        code_verifier (str):        A high-entropy cryptographic random string
        device_code (str):          Code for authorising the device
        filepath_to_upload (str):   Path of sample zip file to upload
        sample_name (str):          Name of sample for upload
        logger (object):            Python logging object
        encoded_clientid (str):     Encoded client_id:client_secret as base64
        access_token (str):         QCII API access token

    Methods
        encode_clientid()
            Encode client_id:client_secret as base64
        generate_access_token()
            Generate access token for use in uploading samples
        upload_sample()
            Make API call to upload sample to QCII
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        code_verifier: str,
        device_code: str,
        filepath_to_upload: str,
        logger: logging.Logger,
    ):
        """
        Constructor for the UploadToQiagen class
            :param client_id (str):             The client for which the code is requested
                                                (provided by QIAGEN)
            :param client_secret (str):         Secret key known only to the application and
                                                the authorization server (provided by QIAGEN)
            :param code_verifier (str):         A high-entropy cryptographic random string
            :param device_code (str):           Code for authorising the device
            :param filepath_to_upload (str):    Path of sample zip file to upload
            :param logger (object):             Python logging object
        """
        self.code_verifier = code_verifier
        self.device_code = device_code
        self.filepath_to_upload = filepath_to_upload
        self.logger = logger
        self.logger.info("Calling UploadToQiagen class")
        self.encoded_clientid = self.encode_clientid(client_id, client_secret)
        self.access_token = self.generate_access_token()
        self.upload_sample()

    def encode_clientid(self, client_id, client_secret) -> str:
        """
        Encode client_id:client_secret as base64
            :param client_id (str):     The client for which the code is requested
                                        (provided by QIAGEN)
            :param client_secret (str): Secret key known only to the application and
                                        the authorization server (provided by QIAGEN)
            :return (str):              Encoded client_id:client_secret as base64
        """
        try:
            self.logger.info("Encoding client_id:client_secret as base64")
            return bytes.decode(
                base64.b64encode(bytes(f"{client_id}:{client_secret}", "utf-8"))
            )
        except Exception as exception:
            self.logger.exception(
                "An exception was encountered when encoding the "
                f"client_id:secret as base64: {exception}"
            )
            sys.exit(1)

    def generate_access_token(self) -> str:
        """
        Generate access token for use in uploading samples
            :return (str):  QCII API access token
        """
        try:
            self.logger.info("Building the access token generation command")
            access_token_cmd = (
                f'curl -i -X POST -H "Authorization: Basic {self.encoded_clientid}"'
                " -d 'grant_type=urn:ietf:params:oauth:grant-type:device_code&device_code="
                f"{self.device_code}&code_verifier={self.code_verifier}' "
                "'https://apps.qiagenbioinformatics.eu/qiaoauth/oauth/token'"
            )
            self.logger.info("Executing the access token generation command")
            out = toolbox.execute_subprocess_command(access_token_cmd, self.logger)
            return out["access_token"]
        except Exception as exception:
            self.logger.exception(
                "An exception was encountered when executing the access "
                f"token generation command: {exception}"
            )
            sys.exit(1)

    def upload_sample(self) -> None:
        """
        Make API call to upload sample to QCII
            :return None:
        """
        try:
            self.logger.info("Building the command to upload the sample to QCII")
            sample_upload_cmd = (
                'curl -X POST -H "Authorization: %s" -H "accept: application/json" -H '
                '"Content-Type: multipart/form-data" -F "file=@%s;type=application/zip" '
                '"https://api.qiagenbioinformatics.eu/v2/sample"'
                % (self.access_token, self.filepath_to_upload)
            )
            self.logger.info("Executing the command to upload the sample to QCII")
            toolbox.execute_subprocess_command(sample_upload_cmd, self.logger)
            self.logger.info("Sample upload was successful")
        except Exception as exception:
            self.logger.error(
                "An error was encountered when executing the QCII sample upload "
                f"command: {exception}."
            )
            sys.exit(1)
