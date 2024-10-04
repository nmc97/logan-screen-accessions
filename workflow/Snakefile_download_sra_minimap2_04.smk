# Load configuration
from common import read_list, temp_or_not, get_layout

configfile: "config.yaml"

base_dir = config["base_dir"]
keep_fastq = config.get("keep_fastq", False)
keep_sra = config.get("keep_sra", False)
accession_list = read_list(config["metrics_file"])

# Register storage provider
storage:
    provider="s3",
    bucket="sra-pub-run-odp",
    prefix="sra/",
    no_sign_request=True,
    max_requests_per_second=10

# Set rule that needs to be fulfilled for pipeline to end
rule all:
    input:
        f"{base_dir}/metrics/summary.txt"

# If output directory doesn't exist, create it
rule create_base_dir:
    output:
        directory(base_dir)
    shell:
        """
        mkdir -p {output}
        """

# Create metrics directory
rule create_metrics_dir:
    input:
        base_dir
    output:
        directory(f"{base_dir}/metrics")
    shell:
        """
        echo "making directory {output}"
        mkdir -p {output}
        touch {output}/test_file.txt
        """

# Create a directory for downloaded SRA data to be stored
# If keep_sra is FALSE, this will be deleted
rule create_sra_dir:
    input:
        base_dir
    output:
        temp_or_not(directory(f"{base_dir}/sra"), keep_sra)
    shell:
        "mkdir -p {output}"

# Create a directory for FASTQ data to be stored
# If keep_fastq is FALSE, this will be deleted
rule create_fastq_dir:
    input:
        base_dir
    output:
        temp_or_not(directory(f"{base_dir}/fastq"), keep_fastq)
    shell:
        "mkdir -p {output}"

# Download accession if available and store in directory base_dir/sra
rule download:
    params:
        accession=lambda wildcards: wildcards.accession
    output:
        temp_or_not(f"{base_dir}/sra/{{accession}}.sra", keep_sra)
    shell:
        """
        aws s3 cp s3://sra-pub-run-odp/sra/{params.accession}/{params.accession} {output} --no-sign-request
        touch {output} # Ensure the file exists even if download fails
        """

# Split SRA file into forward and reverse reads
rule split_reads:
    input:
        sra=f"{base_dir}/sra/{{accession}}.sra"
    output:
        forward=temp_or_not(f"{base_dir}/fastq/{{accession}}_R1.fastq.gz", keep_fastq),
        reverse_reads=temp_or_not(f"{base_dir}/fastq/{{accession}}_R2.fastq.gz", keep_fastq)
    run:
        layout = get_layout(wildcards.accession)
        if layout == "PAIRED":
            shell("""
                fastq-dump --split-files --gzip {input.sra} -O {base_dir}/fastq
                mv {base_dir}/fastq/{wildcards.accession}_1.fastq.gz {output.forward}
                mv {base_dir}/fastq/{wildcards.accession}_2.fastq.gz {output.reverse_reads}
            """)
        elif layout == "SINGLE":
            shell("""
                fastq-dump --gzip {input.sra} -O {base_dir}/fastq
                mv {base_dir}/fastq/{wildcards.accession}.fastq.gz {output.forward}
                touch {output.reverse_reads}  # Create an empty file for reverse read
            """)

# Run minimap2 with downloaded contigs against query fasta
rule run_minimap2:
    input:
        fasta=config["fasta"],
        forward=f"{base_dir}/fastq/{{accession}}_R1.fastq.gz",
        reverse_reads=f"{base_dir}/fastq/{{accession}}_R2.fastq.gz"
    output:
        f"{base_dir}/logan_minimap2/{{accession}}.minimap2_output"
    shell:
        """
        minimap2 -t 8 -a {input.fasta} {input.forward} {input.reverse_reads} \
        | samtools view -hF4 - \
        > {output}
        """

# Calculate metrics
rule calculate_metrics:
    input:
        bam=f"{base_dir}/logan_minimap2/{{accession}}.minimap2_output"
    output:
        f"{base_dir}/metrics/{{accession}}.metrics.txt"
    shell:
        """
        python workflow/calculate_metrics.py {input.bam} {wildcards.accession} > {output}
        """

# Aggregate metrics
rule aggregate_metrics:
    input:
        expand(f"{base_dir}/metrics/{{accession}}.metrics.txt", accession=accession_list)
    output:
        f"{base_dir}/metrics/summary.txt"
    shell:
        """
        cat {input} > {output}
        """

# If `snakemake help` is run
rule help:
    run:
        shell("python help.py")

