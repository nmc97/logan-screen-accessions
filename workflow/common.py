from snakemake.io import temp
import xml.etree.ElementTree as ET
import subprocess

# common.py
def read_list(file):
    with open(file) as f:
        return [line.strip() for line in f]

def temp_or_not(path, keep_temp):
    return path if keep_temp else temp(path)

def get_layout(accession):
    try:
        # Fetch the XML metadata for the accession
        result = subprocess.run(
            f"esearch -db sra -query {accession} | efetch -format xml",
            capture_output=True,
            text=True,
            shell=True
        )
        # Check if the result is empty
        if not result.stdout.strip():
            raise ValueError(f"No XML content returned for accession {accession}")
        
        # Parse the XML content
        root = ET.fromstring(result.stdout)
        layout = root.find(".//LIBRARY_LAYOUT")
        
        if layout.find("PAIRED") is not None:
            return "PAIRED"
        elif layout.find("SINGLE") is not None:
            return "SINGLE"
        else:
            raise ValueError(f"Unknown layout for accession {accession}")
    except Exception as e:
        print(f"Error fetching or parsing XML for accession {accession}: {e}")
        raise
