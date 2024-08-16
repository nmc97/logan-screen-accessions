def print_help():
    help_text = """
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

    """
    print(help_text)

if __name__ == "__main__":
    print_help()
