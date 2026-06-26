import shutil
from typing import List
from entities import Algorithm

def available_algorithms() -> List[Algorithm]:
    print("Checking available algorithms in PATH...")
    algos = []

    # BASELINES
    if shutil.which("gzip"):
        algos.append(Algorithm("gzip", 
            "gzip -c {input} > {output}", 
            "gzip -dc {input} > {output}", 
            ".gz"))
    if shutil.which("bzip2"):
        algos.append(Algorithm("bzip2", 
            "bzip2 -c {input} > {output}", 
            "bzip2 -dc {input} > {output}", 
            ".bz2"))

    # ALGORITMES ESPECÍFICS PER ADN
    if shutil.which("genozip") and shutil.which("genounzip"):
        algos.append(Algorithm("genozip", 
            "genozip --output {output} {input}", 
            "genounzip --output {output} {input}", 
            ".genozip"))
    if shutil.which("MFCompressC") and shutil.which("MFCompressD"):
        algos.append(Algorithm("mfcompress", 
            "MFCompressC -2 -o {output} {input}", 
            "MFCompressD -o {output} {input}", 
            ".mfc"))
    if shutil.which("ennaf") and shutil.which("unnaf"):
        algos.append(Algorithm(
            "naf",
            "ennaf --temp-dir {temp_dir} -15 {input} -o {output}",
            "unnaf {input} -o {output}",
            ".naf"
        ))   

    # ALGORITMES AMB XARXES NEURONALS / CONTEXT MIXING
    if shutil.which("GeCo3") and shutil.which("GeDe3"):
        algos.append(Algorithm("geco3", 
            "GeCo3 -v {input}", 
            "GeDe3 {input}", 
            ".co"))
    if shutil.which("paq8l"):
        algos.append(Algorithm("paq8l", 
            "paq8l -1 {input} {output}", 
            "paq8l -d {input} {output_dir}", 
            ".paq8l"))

    return algos
