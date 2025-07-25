# Snakemake pipeline for screening LOGAN with minimap2
[![DOI](https://zenodo.org/badge/843377272.svg)](https://doi.org/10.5281/zenodo.16418927)

This is a snakemake pipeline for screening the LOGAN database for a query sequence using minimap2.

## Set up 
### Mamba environment

Dependencies (version tested):

- snakemake (9.8.1)
- awscli (2.27.58)
- samtools (1.22.1)
- python (3.12.11)
- minimap2 (2.30)
- pysam (0.23.3)
- snakemake-storage-plugin-s3 (0.3.3)
- sra-tools (3.2.1) (needed only to run the pipeline on raw reads after first screen with logan assemblies)
- entrez-direct (24.0) (same as above)

#### Create mamba environment:

``` bash
mamba create -n logan_snakemake -c conda-forge -c bioconda snakemake awscli minimap2 samtools snakemake-storage-plugin-s3 pysam sra-tools entrez-direct
```

### AWS environmental variables

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

- Prepare accessions file 

- Edit config file `config.yaml` with correct file paths and specify if downloaded contigs should be kept:

``` bash
base_dir: "./"
list_file: "/path/to/list_of_accessions.txt"
fasta: "/path/to/query.fasta"
keep_temp: FALSE
```

- Run pipeline and optionally specify cores:

``` bash
snakemake --cores 6
```

- You can specify paths to the snakemake file and config file:

``` bash
snakemake -s /path/to/Snakefile --configfile /path/to/config.yaml
```

- If the job gets interrupted you can use `--rerun-incomplete` to start again with the accessions that were not completed properly:

``` bash
snakemake --cores 6 --rerun-incomplete
```

#### basic help file 

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

#### Test

```bash
snakemake --cores 2 --configfile ./test/config.test.yaml 
```
OR specify the snakemake workflow file:
```bash
snakemake --cores 2 -s ./workflow/Snakefile --configfile ./test/config.test.yaml  
```

## Output files

Results will be stored in "base_dir" as specified in config file.

### Downloaded assemblies
Logan assemblies will be downloaded into:
`$base_dir/data`
You can change the setting `keep_temp` to keep or remove these files after running minimap2.

### Minimap output
Minimap outputs will be stored in: 
`$base_dir/logan_minimap2`

### Metrics calculated
Some calculations are made using Samtools to determine the coverage of each samples over the query
A metrics folder will be made with individual metrics files and a summary file:
 `$base_dir/metrics/summary.txt`

example summary.txt:
``` bash
ERR10144421     3407    0.38    3407    0.38
SRR19201055     889035  98.82   882276  98.07
```

Columns are sample_name, coverage, coverage pc, covered bases, covered bases pc 

### Running sra download script

- Prepare accessions file 

- Ensure sra-tools is availble in your conda environment

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

- Outputs files will be saved in $base_dir (ideally this should be different from the base directory of the logan output, e.g. `test/sra`)

### Test sra download workflow

``` bash 
snakemake --cores 2 -s ./workflow/Snakefile_download_sra_minimap2.smk --configfile ./test/config.test_sra.yaml 
```

Result:
``` bash
ERR10144421     92447   10.28   6066    0.67
SRR19201055     94555444        10510.76        765643  85.11
```

# To DO

1. Change how it handles accessions with no corresponding data in the logan s3 bucket
   1. at the moment it creates an empty file
   2. maybe better to remove these from the accession list before processing them so the pipeline doesn't require outputs to move on
2. Think about how it deals with logs
3. Add *Diamond* option and make minimap2 optional
4. Parse output files and summarise
5. Change it so that it can be run from anywhere
6. Move scripts out of workflow directory into scripts directory
7. Write it so that it builds mamba environments within rules (maybe not neccessary in this case)
8. Consider changing minimap to deal with contigs using `-x asm5`
9. Change how it calculates metrics (tools availible for this)
10. Think about removing more files if needed
11. Consider how it could work for multiple query sequences (saves downloading the same thing over and over again for different queries)
12. Figure out why the LAYOUT finding doesn't always work well

## More about Logan
**GitHub:** https://github.com/IndexThePlanet/Logan
**Preprint:** https://www.biorxiv.org/content/10.1101/2024.07.30.605881v1
**Citation:** "Logan: Planetary-Scale Genome Assembly Surveys Life’s Diversity
Rayan Chikhi, Brice Raffestin, Anton Korobeynikov, Robert Edgar, Artem Babaian
bioRxiv 2024.07.30.605881; doi: https://doi.org/10.1101/2024.07.30.605881
