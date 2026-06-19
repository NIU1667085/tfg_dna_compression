#!/usr/bin/env python3
import csv
import hashlib
import math

from pathlib import Path
from typing import Optional
from  dataclasses import asdict
from typing import List
from fasta_utils import count_header_symbols
from entities import ResultRow, Dataset

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

def mbps(num_bytes: int, seconds: float) -> float:
    if seconds <= 0:
        return 0.0
    return (num_bytes / (1024 * 1024)) / seconds

def shannon_entropy_from_counts(counts: dict[str, int]) -> Optional[float]:
    """
    Entropia de Shannon d'ordre 0, en bits per símbol: H = -sum p_i log2(p_i).
    Retorna None si no hi ha símbols.
    """
    total = sum(counts.values())
    if total == 0:
        return None

    entropy = 0.0
    for count in counts.values():
        if count == 0:
            continue
        p = count / total
        entropy -= p * math.log2(p)
    return entropy

def compute_dataset_entropies(fasta_path: Path, base_counts: dict[str, int]) -> dict[str, Optional[float]]:

    # (a) ACGT
    acgt_counts = {k: base_counts.get(k, 0) for k in "ACGT"}

    # (b) ACGTN
    acgtn_counts = {k: base_counts.get(k, 0) for k in "ACGTN"}

    # (c) tots els símbols de seqüència (inclou unknown si el tens)
    seq_all_counts = acgtn_counts.copy()
    for k, v in base_counts.get("unknown", {}).items():
        seq_all_counts[k] = v

    # (d) seq + headers
    header = count_header_symbols(fasta_path)
    for k, v in header.items():
        seq_all_counts[k] = seq_all_counts.get(k, 0) + v
    header_counts = seq_all_counts.copy()
    
    return {
        "entropy_acgt": shannon_entropy_from_counts(acgt_counts),
        "entropy_acgtn": shannon_entropy_from_counts(acgtn_counts),
        "entropy_seq_all": shannon_entropy_from_counts(seq_all_counts),
        "entropy_seq_headers": shannon_entropy_from_counts(header_counts),
        "header_counts": header_counts
    }

def extract_sequence(path: Path) -> str:
    seq = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if not line.startswith(">"):
                seq.append(line.strip().upper())
    return "".join(seq)

def remove_N(seq: str) -> str:
    return seq.replace("N", "")

def remove_unknown(seq: str) -> str:
    return "".join(base for base in seq if base in "ACGT")

def write_csv(rows: List[ResultRow], out_csv: Path):
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        w.writeheader()
        for r in rows:
            w.writerow(asdict(r))