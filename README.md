# Snakemake pipeline for screening LOGAN with minimap2

This is a snakemake pipeline for screening the LOGAN database for a query sequence using minimap2.

## Set up 
### Mamba environment

Dependencies (need to chack versions that currently work)

- snakemake
- aws
- samtools
- python
- minimap2
- pysam
- snakemake-storage-plugin-s3
- seqkit (can't remember if this is needed but could use later on)

 mamba environment (need to check this works)

``` bash
mamba create -n logan_snakemake -c conda-forge -c bioconda  snakemake awscli minimap2 samtools seqkit snakemake-storage-plugin-s3 pysam sra-tools
```

Set AWS environmental variables to null
Add aws region as `us-west-2`

``` bash
export SNAKEMAKE_STORAGE_S3_ACCESS_KEY="null"
export SNAKEMAKE_STORAGE_S3_SECRET_KEY="null"
export AWS_ACCESS_KEY_ID="null"
export AWS_SECRET_ACCESS_KEY="null"
export AWS_DEFAULT_REGION=us-west-2
```

## Basic usage:

Edit config file `config.yaml` with correct file paths and specify if downloaded contigs should be kept:

``` bash
base_dir: "./"
list_file: "/path/to/list_of_accessions.txt"
fasta: "/path/to/query.fasta"
keep_temp: FALSE
```

Run pipeline and optionally specify cores:

``` bash
snakemake --cores 6
```

You can specify paths to the snakemake file and config file:

``` bash
snakemake -s /path/to/Snakefile --configfile /path/to/config.yaml
```

If the job gets interrupted you can use `` to start again with the accessions that were not completed properly:

``` bash
snakemake --cores 6 --rerun-incomplete
```

Use `snakemake help` to display help:

```bash 
Usage: snakemake [OPTIONS]

    Options:
      --cores INT       Number of cores to use.
      --config FILE     Path to the config file.
      --snakefile FILE  Path to the Snakefile.
      --help            Show this help message and exit.

    Example:
      snakemake --cores 4 --config config.yaml

    Pipeline Description:
      This pipeline performs the following steps:
      1. Creates output directory as specficed in config file as base_dir.
      2. Downloads contig files from S3 from a list of accessions provided.
      3. Runs Minimap2 to align sequences.
      4. Optionally removes downloaded contig files

    Configuration in config.yaml:
      - base_dir: Base directory for outputs.
      - keep_temp: Whether to keep temporary files.
      - list_file: File containing list of accessions.
      - fasta: Path to the reference fasta file.

    Run test files:
      snakemake --cores 1 --configfile test/config.test.yaml
```

## Output files

Results will be stored in "base_dir"

### Downloaded assemblies
Logan assemblies will be downloaded into:
`$base_dir/data`
You can change the setting keep_temp to keep or remove these files after running minimap2.

### Minimap output
Minimap outputs will be stored in: 
`$base_dir/logan_minimap2`

### Metrics calculated
Some calculations are made to determine the coverage of each samples over the query
A metrics folder will be made with individual metrics files and a summary file:
 `$base_dir/metrics/summary.txt`

example summary.txt:
``` bash
ERR10144421     92447   10.28   6066    0.67
SRR19201055     94555444        10510.76        765643  85.11
```

Columns are sample_name, coverage, coverage pc, cover 

### Running sra download script

- Prepare accessions file 

- Ensure sra-tools is availible in your conda environment

- Edit or create a new config file e.g.:
``` bash
base_dir: "test/sra"
metrics_file: "test/accessions.txt"
fasta: "test/plasmid.fasta"
keep_fastq: TRUE
keep_sra: FALSE
```

- Run pipeline `Snakefile_download_sra_minimap2.smk`

``` bash
snakemake -s /path/to/Snakefile_download_sra_minimap2.smk --configfile /path/to/config.yaml
```

# To DO

1. Change how it handles accessions with no corresponding data in the logan s3 bucket
   1. at the moment it creates an empty file
   2. maybe better to remove these from the accession list before processing them so the pipeline doesn't require outputs to move on
2. Think about how it deals with logs
3. Add Diamond option and make minimap2 optional
4. Parse output files and summarise
5. Change it so that it can be run from anywhere
6. Move scripts out of workflow directory into scripts directory
7. Write it so that it builds mamba environments within rules (maybe not neccessary in this case)
8. Consider changing minimap to deal with contigs using `-x asm5`
9. Change how it calculates metrics
10. think about removing more files if needed
11. Consider how it could work for multiple query sequences (saves downloading the same thing over and over again)
