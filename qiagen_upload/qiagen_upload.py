""" qiagen_upload.py

Upload the zip file containing the XML file to QCII
"""
import pkce
import base64
import subprocess
import argparse
import json
import xml.etree.ElementTree as etree
import os
import shutil
import zipfile
import glob

# TODO add error handling
# TODO add logging

class AddXMLtoZIP():
    """
    Class to Add the XML for the QCI sample upload to the input ZIP file

    Attributes
        sample_name (str):                  Sample name
        sample_zip_folder (str):            Zip folder containing variant files
        xml_outfile (str):                  XML output file
        sample_zip_folder_with_xml (str):   Zip folder containing variant files and XML

    Methods
        add_file_to_zip (zip_folder_path, file_path)
            Create new output zip file, and add XML file
    """
    def __init__(self, sample_name: str, sample_zip_folder: str):
        """
        Constructor for the AddXMLtoZIP class
            :param sample_name (str):          Sample name
            :param sample_zip_folder (str):    Zip folder containing variant files
        """
        self.sample_name = sample_name
        self.sample_zip_folder = sample_zip_folder
        self.xml_outfile = CreateXML(sample_name).xml_outfile
        self.outdir = os.path.join(os.getcwd(), 'outputs')
        self.outdir_sample_folder = os.path.join(self.outdir, self.sample_name)
        self.output_zip = os.path.join(self.outdir, f"{self.sample_name}.zip")
        self.files_to_zip = self.extract_zip_contents()
        self.write_output_zip()
        
    def extract_zip_contents(self) -> None:
        """
        Extract contents of input sample zip
            :return None:
        """
        with zipfile.ZipFile(self.sample_zip_folder, mode="r") as archive:
            for file in archive.namelist():
                archive.extract(file, self.outdir)
        for file in os.listdir(self.outdir_sample_folder):
            shutil.move(
                os.path.join(self.outdir_sample_folder, file),
                os.path.join(self.outdir, file)
            )
        os.rmdir(self.outdir_sample_folder)
        return os.listdir(self.outdir)

    def write_output_zip(self) -> None:
        """
        Create new output zip file, containing all original files
        without directory, plus output XML file
        """
        with zipfile.ZipFile(self.output_zip, 'w') as zip_ref:
            for file in self.files_to_zip:
                filepath = os.path.join(self.outdir, file)
                zip_ref.write(filepath, arcname=file)

# TODO add error handling
# TODO add logging
class CreateXML():
    """
    Class to create the XML for the QCI sample upload

    Attributes
        sample_name (str):                  Sample name
        xml_template (str):                 Path to XML template for QCI sample upload
        combinedvariants_tsv (str):         Path to TSV CombinedVariantOutput file
        copynumbervariants_vcf (str):       Path to VCF CopyNumberVariants file
        mergedvariants_vcf (str):           Path to VCF MergedSmallVariants file
        tmb_tsv (str):                      Path to TSV TML Trace file
        mergedvariantsannotated_json (str): Path to merged annotated variants zip file
        outdir (str):                       Directory for output files
        xml_outfile (str):                  XML file created by the script
        variants_filenames (list):          List of filenames to be included in the
                                            VariantsFilename subelement within the
                                            VariantsFilenames subelement in the XML file
        xml_root (etree.Element):           XML template data at root level
        sample_element (etree.Element):     XML Sample element
        variantsfilenames_sub
        (etree.Element):                    XML VariantsFilenames element

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
            Add sample ID subelement to Sample element
        add_variants_filenames()
            Add VariantsFilename subelement to XML for each file that requires upload to
            QCII for the sample
        order_elements()
            Order elements so that they are in alphabetical descending order, as expected by
            the QCII API
        write_to_outfile()
            Write constructed XML to output file
    """
    def __init__(self, sample_name: str):
        """
        Constructor for the CreateXML class
            :param sample_name (str):           Name of sample for upload
        """
        etree.register_namespace('', "http://qci.qiagen.com/xsd/interpret")
        self.sample_name = sample_name
        self.xml_template = os.path.join(
            os.getcwd(), "templates", "sample_upload_template.xml"
        )
        self.combinedvariants_tsv = f'{self.sample_name}_CombinedVariantOutput.tsv'
        self.copynumbervariants_vcf = f'{self.sample_name}_CopyNumberVariants.vcf'
        self.mergedvariants_vcf = f'{self.sample_name}_MergedSmallVariants.genome.vcf'
        self.tmb_tsv = f'{self.sample_name}_TMB_Trace.tsv'
        self.mergedvariantsannotated_json = f'{self.sample_name}_MergedVariants_Annotated.json.gz'
        self.outdir = os.path.join(os.getcwd(), 'outputs')
        self.xml_outfile = os.path.join(self.outdir, f'{self.sample_name}.xml')
        self.variants_filenames = [
            self.combinedvariants_tsv, self.copynumbervariants_vcf,
            self.mergedvariants_vcf, self.tmb_tsv,
            # self.mergedvariantsannotated_json
        ]
        self.xml_root = self.import_xml_data()
        self.sample_element = self.get_xml_element('Sample')
        self.variantsfilenames_sub = self.get_sample_subelement('VariantsFilenames')
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
        return etree.parse(self.xml_template).getroot()

    def get_xml_element(self, element_name) -> etree.Element:
        """
        Extract an XML element from the xml root
            :param element_name (str):  Name of element to be extracted
            :return (etree.Element):    
        """
        return self.xml_root.find('{http://qci.qiagen.com/xsd/interpret}' + f'{element_name}')

    def get_sample_subelement(self, subelement) -> etree.Element:
        """
        Extract a subelement from within the sample element
            :param subelement:              
            :return  etree.Element object:  XML VariantsFilenames element
        """
        return self.sample_element.find('{http://qci.qiagen.com/xsd/interpret}' + f'{subelement}')

    def add_sample_name(self) -> None:
        """
        Add sample name subelement to Sample element
            :return None:
        """
        name_subelement = etree.SubElement(self.sample_element, 'Name')
        name_subelement.text = self.sample_name

    def add_sample_subjectid(self) -> None:
        """
        Add sample ID subelement to Sample element
            :return None:
        """
        subjectid_subelement = etree.SubElement(self.sample_element, 'SubjectId')
        subjectid_subelement.text = self.sample_name

    def add_variants_filenames(self) -> None:
        """
        Add VariantsFilename subelement to XML for each file that requires upload to
        QCII for the sample
            :return None:
        """
        for filename in self.variants_filenames:
            VariantsFilename = etree.SubElement(
                self.variantsfilenames_sub, 'VariantsFilename'
            )
            VariantsFilename.text = filename

    def order_elements(self) -> None:
        """
        Order elements so that they are in alphabetical descending order, as expected by
        the QCII API
            :return None:
        """
        # Sort the first layer
        self.xml_root[:] = sorted(self.xml_root, key=lambda child: (child.tag,child.get('name')))
        # Sort the second layer
        for c in self.xml_root:
            c[:] = sorted(c, key=lambda child: (child.tag,child.get('desc')))

    def write_to_outfile(self) -> None:
        """
        Write constructed XML to output file
            :return None:
        """
        if not os.path.exists(self.outdir):
            os.mkdir(self.outdir)
        with open(self.xml_outfile, "w", encoding="utf-8") as output:
            output.write(etree.tostring(self.xml_root).decode())


class UploadToQiagen():
    """
    Class to upload the created zip file to QCII using the API

    Attributes
        code_verifier

        device_code
        filepath
        sample_name
        encoded_clientid
        access_token

    Methods
        encode_clientid()
        generate_access_token()
        upload_sample()
    """
    def __init__(self, client_id, client_secret, code_verifier, device_code, filepath, sample_name):
        """
        """
        self.code_verifier = code_verifier
        self.device_code = device_code
        self.filepath = filepath
        self.sample_name = sample_name
        self.encoded_clientid = self.encode_clientid(client_id, client_secret)
        self.access_token = self.generate_access_token()
        self.upload_sample()

    def encode_clientid(self, client_id, client_secret):
        """
        Encode client_id:client_secret
        """
        return bytes.decode(base64.b64encode(bytes(f'{client_id}:{client_secret}', 'utf-8')))

    def generate_access_token(self):
        """
        Generate access token for use in uploading samples
        """
        access_token_cmd = (
            f"curl -i -X POST -H \"Authorization: Basic {self.encoded_clientid}\""
            " -d 'grant_type=urn:ietf:params:oauth:grant-type:device_code&device_code="
            f"{self.device_code}&code_verifier={self.code_verifier}' "
            "'https://apps.qiagenbioinformatics.eu/qiaoauth/oauth/token'"
            )
        json_response = subprocess.Popen([access_token_cmd], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        out, _ = json_response.communicate()
        return json.loads(out.decode('utf-8').splitlines()[-1])['access_token']

    def upload_sample(self):
        """
        Make API call to upload sample to QCII
            :param access_token (str):  Access token generated by generate_access_token
        """
        sample_upload_cmd = (
            'curl -X POST -H "Authorization: %s" -H "accept: application/json" -H '
            '"Content-Type: multipart/form-data" -F "file=@%s;type=application/zip" '
            '"https://api.qiagenbioinformatics.eu/v2/sample"' % (self.access_token, self.filepath)
            )
        print(sample_upload_cmd)
        json_response = subprocess.Popen([sample_upload_cmd], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        out, err = json_response.communicate()
        print(f"OUT: {out}")
        print(f"ERR: {err}")
        # response = json.loads(out.decode('utf-8').splitlines()[-1])['access_token']
