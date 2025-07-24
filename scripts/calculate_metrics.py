import pysam
import sys
import subprocess
import os

def sort_and_index_bam(bamfile_path):
    sorted_bamfile_path = bamfile_path.replace(".bam", ".sorted.bam")
    # Sort the BAM file
    subprocess.run(["samtools", "sort", "-o", sorted_bamfile_path, bamfile_path], check=True)
    # Index the sorted BAM file
    subprocess.run(["samtools", "index", sorted_bamfile_path], check=True)
    return sorted_bamfile_path

def calculate_coverage(bamfile_path):
    bamfile = pysam.AlignmentFile(bamfile_path, "rb")
    total_length = sum(bamfile.lengths)
    #total_length = sum([seq.length for seq in bamfile.header.references])
    coverage_bases = sum([pileupcolumn.n for pileupcolumn in bamfile.pileup()])
    coverage = (coverage_bases / total_length) * 100
    covered_bases = 0
    for pileupcolumn in bamfile.pileup():
        # Check if the position is covered by at least one read
        if pileupcolumn.n > 0:
            covered_bases += 1
    covered_bases_pc = (covered_bases / total_length) * 100
    bamfile.close()
    return coverage_bases, coverage, covered_bases, covered_bases_pc

if __name__ == "__main__":
    bamfile_path = sys.argv[1]
    accession = sys.argv[2]
    sorted_bamfile_path = sort_and_index_bam(bamfile_path)

    coverage_bases, coverage, covered_bases, covered_bases_pc = calculate_coverage(sorted_bamfile_path)
    print(f"{accession}\t{coverage_bases}\t{coverage:.2f}\t{covered_bases}\t{covered_bases_pc:.2f}")
