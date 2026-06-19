
import hashlib
import os
from pathlib import Path
import json
import json
import sys
import math
from datetime import datetime

CHARS = "ACGT"
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "data_aux"
RESULTS_DIR = ROOT / "results" / "2026_06_19_22_13_59"
META_DIR = DATA_DIR / "geco3"

def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """
    Calcula empremta digital SHA-256 d'un fitxer llegint-lo en trossos per evitar carregar-lo tot a la memòria.
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def file_size(path: Path) -> int:
    return path.stat().st_size

def preprocess_fasta(data_path, file):
    """
    Llegeix el fitxer FASTA guardant capçaleres i caràcters modificats
    per garantir una descompressió idèntica.
    """
    # Guardem la capçalera original (p.ex: >chrM)
    raw_seq = ""
    header = ""
    with open(data_path, "r", encoding="utf-8", errors="ignore") as f:
        header_line = f.readline()
        if not header_line.startswith(">"):
            print(f"Error: El fitxer {data_path} no sembla ser un FASTA vàlid (no comença per >).")
            sys.exit(1)

        header = header_line

        for line in f:
            if line.startswith(">"):
                print(f"Error: El fitxer {data_path} sembla ser un multi-FASTA, cosa que no està suportada.")
                sys.exit(1)

            raw_seq += line.strip()

    metadata_log = []
    cleaned_sequence = []

    # Processat caràcter per caràcter d'acord amb els chars admessos (chars="ACGT")
    for idx, char in enumerate(raw_seq):
        if char in CHARS:
            cleaned_sequence.append(char)
        else:
            # Guardem la posició i el caràcter original (minúscules, N, wildcards...)
            metadata_log.append((idx, char))

    cleaned_text = "".join(cleaned_sequence)

    if file:
        with open(file, "w", encoding="utf-8") as out_f:
            metadata = {
                "header": header,
                "metadata_log": metadata_log
            }
            json.dump(metadata, out_f, ensure_ascii=False, indent=2)

from pathlib import Path

       
def postprocess_fasta(cleaned_text, file, output):
    if file is None:
        raise ValueError("Cal metadata_log o file amb metadata")

    with open(file, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    metadata_log = metadata["metadata_log"]
    header = metadata["header"]

    # assegurem ordre
    metadata_log = sorted(metadata_log, key=lambda x: x[0])

    seq_list = list(cleaned_text)
    # Substitució directa lossless per índex
   
    for idx, original_char in metadata_log:
        if idx < len(seq_list):
            seq_list.insert(idx, original_char)
    original_sequence = "".join(seq_list)

    os.makedirs(output, exist_ok=True)
    base_name = os.path.basename(file).replace('.json', '.fasta')
    output_file_path = os.path.join(output, base_name)
    print(file)
    print(output_file_path)

    # escriu el fitxer (es crea si no existeix)
    with open(output_file_path, "w", encoding="utf-8") as out_f:
        out_f.write(header)
        for i in range(0, len(original_sequence), 70):
            out_f.write(original_sequence[i : i + 70] + "\n")



if __name__ == "__main__":
    
    for fasta_path in sorted(DATA_DIR.rglob("*")):
        # if not_run in fasta_path.parts:
        #     continue
        print(fasta_path)
        # if not fasta_path.is_file() or "chr" in fasta_path.name:
        #     continue 
        
        aux_dir = META_DIR / fasta_path.resolve().parents[0].name
        aux_dir.mkdir(parents=True, exist_ok=True)
        aux_path = aux_dir / fasta_path.name
        metadata_path = aux_path.with_suffix(".json")
        geco3_path = RESULTS_DIR / "decompressed" / fasta_path.name[:-6] / "geco3" / fasta_path.name
        
        preprocess_fasta(fasta_path, metadata_path)
        print(f"\t{file_size(fasta_path)}, m: {file_size(metadata_path)}, t: {file_size(geco3_path) + file_size(metadata_path)}")

        final_path = META_DIR / "final"
        lossless_path = final_path / fasta_path.name
        with open(
            geco3_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:
            cleaned_text = f.read().strip()
        postprocess_fasta(cleaned_text, metadata_path, final_path)

        print(f"[*] Processat {fasta_path.name} amb metadades a {metadata_path.name}")
        print(f"\t{file_size(fasta_path)}, m: {file_size(metadata_path)}, t: {file_size(geco3_path) + file_size(metadata_path)}")
        print(f"\t{file_size(lossless_path)},  {sha256_file(fasta_path) == sha256_file(lossless_path)}")