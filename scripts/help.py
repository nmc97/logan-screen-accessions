def print_help():
    help_text = """
    Usage: snakemake [OPTIONS]

    Options (general snakemake options, see snakemake --help for more):
      -c --cores INT       Number of cores to use.
      --configfile FILE     Path to the config file.
      -C --config  KEY      Overwrite specific config value 
      -s --snakefile FILE  Path to the Snakefile.
      --help            Show this help message and exit.

    Example:
      snakemake --cores 4 --configfile config.yaml

    Pipeline Description:
      This pipeline performs the following steps:
      1. Creates output directory as specficed in config file as base_dir.
      2. Downloads contig files from logan S3 bucket for all accessions in a providede list.
      3. Runs Minimap2 to align sequences.
      4. Optionally removes downloaded contig files

    Configuration in config.yaml:
      - base_dir: [base directory for outputs].
      - keep_temp: [keep temporary files, default no].
      - list_file: [list of accessions, no default].
      - fasta: [path to the query fasta file].

    Run test files:
      snakemake --cores 1 --configfile test/config.test.yaml

    """
    print(help_text)

if __name__ == "__main__":
    print_help()
