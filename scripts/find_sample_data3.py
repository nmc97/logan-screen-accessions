import subprocess
import xml.etree.ElementTree as ET
import csv
import sys

def fetch_and_convert(input_file, output_file):
    # Read the list of SRA accession numbers from the input file
    with open(input_file, 'r') as file:
        sra_accessions = [line.strip() for line in file]

    # Open the output CSV file for writing
    with open(output_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        # Write the header
        header = [
            'Accession', 'Title', 'Organism', 'Taxonomy ID', 'Owner', 'Owner URL', 'Contact First Name', 'Contact Last Name',
            'Model', 'Package', 'Strain', 'Isolate', 'Isolation Source', 'Collected By', 'Collection Date',
            'Geographic Location', 'Latitude and Longitude', 'Host', 'Host Disease', 'Source Type', 'BioProject',
            'Sample Name', 'Food Origin', 'Project Name', 'Sequenced By', 'Comment'
        ]
        csvwriter.writerow(header)
        
        # Process each accession number
        for sra_accession in sra_accessions:
            # Fetch the XML data using esearch, elink, and efetch
            fetch_command = f"esearch -db sra -query {sra_accession} | elink -target biosample | efetch -format xml"
            result = subprocess.run(fetch_command, shell=True, capture_output=True, text=True)
            
            # Check if the result is empty
            if not result.stdout.strip():
                print(f"No data found for {sra_accession}")
                continue
            
            # Parse the fetched XML data
            root = ET.fromstring(result.stdout)
            
            # Iterate through each BioSample and extract relevant information
            for biosample in root.findall('.//BioSample'):
                accession = biosample.get('accession')
                title = biosample.find('.//Title').text if biosample.find('.//Title') is not None else ''
                organism = biosample.find('.//Organism').get('taxonomy_name') if biosample.find('.//Organism') is not None else ''
                taxonomy_id = biosample.find('.//Organism').get('taxonomy_id') if biosample.find('.//Organism') is not None else ''
                owner = biosample.find('.//Owner/Name').text if biosample.find('.//Owner/Name') is not None else ''
                owner_url = biosample.find('.//Owner/Name').get('url') if biosample.find('.//Owner/Name') is not None else ''
                contact_first_name = biosample.find('.//Contact/Name/First').text if biosample.find('.//Contact/Name/First') is not None else ''
                contact_last_name = biosample.find('.//Contact/Name/Last').text if biosample.find('.//Contact/Name/Last') is not None else ''
                model = biosample.find('.//Model').text if biosample.find('.//Model') is not None else ''
                package = biosample.find('.//Package').text if biosample.find('.//Package') is not None else ''
                
                attributes = {attr.get('attribute_name'): attr.text for attr in biosample.findall('.//Attribute')}
                strain = attributes.get('strain', '')
                isolate = attributes.get('isolate', '')
                isolation_source = attributes.get('isolation_source', '')
                collected_by = attributes.get('collected_by', '')
                collection_date = attributes.get('collection_date', '')
                geo_loc_name = attributes.get('geo_loc_name', '')
                lat_lon = attributes.get('lat_lon', '')
                host = attributes.get('host', '')
                host_disease = attributes.get('host_disease', '')
                source_type = attributes.get('source_type', '')
                sample_name = attributes.get('isolate_name_alias', '')
                food_origin = attributes.get('food_origin', '')
                project_name = attributes.get('project_name', '')
                sequenced_by = attributes.get('sequenced_by', '')
                
                comment = biosample.find('.//Comment/Paragraph').text if biosample.find('.//Comment/Paragraph') is not None else ''
                
                bioproject_link = biosample.find(".//Link[@target='bioproject']")
                bioproject = bioproject_link.text if bioproject_link is not None else ''
                
                # Write the row to the CSV file
                csvwriter.writerow([
                    accession, title, organism, taxonomy_id, owner, owner_url, contact_first_name, contact_last_name,
                    model, package, strain, isolate, isolation_source, collected_by, collection_date,
                    geo_loc_name, lat_lon, host, host_disease, source_type, bioproject,
                    sample_name, food_origin, project_name, sequenced_by, comment
                ])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python fetch_and_convert.py <input_file> <output_file>")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        fetch_and_convert(input_file, output_file)

