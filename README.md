# Snakemake pipeline for screening LOGAN with minimap2

This is a snakemake pipeline for screening the LOGAN database for a query sequence using minimap2.

## Mamba environment

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
mamba create -n logan_snakemake -c conda-forge -c bioconda  snakemake awscli minimap2 samtools seqkit snakemake-storage-plugin-s3 pysam
```

Basic usage:

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
# To DO

1. Change how it handles accessions with no corresponding data in the logan s3 bucket
   1. at the moment it creates an empty file
   2. maybe better to remove these from the accession list before processing them so the pipeline doesn't require outputs to move on
2. Think about how it deals with logs
3. Add Diamond option and make minimap2 optional
4. Parse output files and summarise
5. change it so that it can be run from anywhere
6. move scripts out of workflow directory into scripts directory
7. write it so that it builds mamba environments within rules (maybe not neccessary in this case)
8. Change the coverage calculation/ add calculation that specifically counts for each base in the query how many are covered by at least one sequence
