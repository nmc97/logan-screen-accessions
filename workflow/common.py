from snakemake.io import temp

# common.py
def read_list(file):
    with open(file) as f:
        return [line.strip() for line in f]

def temp_or_not(path, keep_temp):
    return path if keep_temp else temp(path)
