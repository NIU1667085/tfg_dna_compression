# datasets.py
from pathlib import Path
from typing import List
from entities import Dataset
from utils import compute_dataset_entropies, shannon_entropy_from_counts, file_size
from fasta_utils import count_fasta_symbols, count_size_header, read_fasta_description, delete_fasta_header

def load_datasets(DATA_DIR: Path) -> List[Dataset]:
    """
    Automatically loads all FASTA files within data,
    including subdirectories such as virus, bacteria, mitochondria, chromosome and genome.
    """
    print(f"Loading datasets from {DATA_DIR}...")
    fasta_extensions = {".fasta", ".fa"} # ".fna"}
    items = []

    #not_run = "chromosome" # "genome" # "chromosome" # "mitochondria" # "bacteria" # "virus"

    for fasta_path in sorted(DATA_DIR.rglob("*")):
        # if not_run in fasta_path.parts:
        #     continue
        if not fasta_path.is_file():
            continue

        if fasta_path.suffix.lower() not in fasta_extensions:
            continue

        dataset_type = fasta_path.parent.name
        dataset_id = fasta_path.stem
        description = read_fasta_description(fasta_path)

        base_counts = count_fasta_symbols(fasta_path)
        num_bases = sum(base_counts[base] for base in "ACGT")
        num_no_std = sum(base_counts.get("unknown", {}).values()) + base_counts.get("N", 0)

        size_header = count_size_header(fasta_path)

        entropies = compute_dataset_entropies(fasta_path, base_counts)
        entropy_acgtn = entropies["entropy_acgtn"]
        entropy_acgt = entropies["entropy_acgt"]
        entropy_seq_all = entropies["entropy_seq_all"]
        entropy_seq_all_headers = entropies["entropy_seq_headers"]
        header_counts = entropies["header_counts"]

        items.append(Dataset(
            dataset_id=dataset_id,
            label=dataset_type,
            description=description,
            fasta_path=fasta_path,
            size_bytes=file_size(fasta_path),
            contains_unknown=(num_no_std > 0),
            num_bases_std=num_bases,
            num_bases_seq=num_bases + num_no_std,
            base_counts=base_counts,
            size_header=size_header,
            header_counts=header_counts,
            entropy_acgtn_bits_per_base=entropy_acgtn, 
            entropy_acgt_bits_per_base=entropy_acgt,
            entropy_seq_all_bits_per_base=entropy_seq_all,
            entropy_seq_all_headers_bits_per_base=entropy_seq_all_headers

        ))

    return items
