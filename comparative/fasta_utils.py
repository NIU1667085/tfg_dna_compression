#!/usr/bin/env python3
from pathlib import Path
from collections import Counter

def count_total_bases(fasta_path: Path) -> int:
    total = 0
    with open(fasta_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if not line.startswith(">"):
                total += sum(1 for ch in line.strip().upper() if ch in "ACGTN")
    return total

def count_N_bases(fasta_path: Path) -> int:
    total = 0
    with open(fasta_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if not line.startswith(">"):
                total += line.upper().count("N")
    return total

def count_size_header(fasta_path: Path) -> int:
    size_header = 0
    with open(fasta_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith(">"):
                size_header += len(line.encode("utf-8"))
            else:
                continue # per considerar tambe multi-fasta
    return size_header

def count_fasta_symbols(fasta_path: Path) -> dict[str, int]:
    """
    Compta els símbols A, C, G, T i N de la seqüència FASTA, ignorant capçaleres i salts de línia.
    """
    accepted_bases = set("ACGTN")

    counts = {base: 0 for base in accepted_bases}
    counts["unknown"] = {}

    with open(fasta_path, "r", encoding="utf-8", errors="ignore") as f:

        for line in f:
            if line.startswith(">"):
                continue

            line = line.strip().upper()

            line_counts = Counter(line)

            for base in accepted_bases:
                counts[base] += line_counts.get(base, 0)

            for ch, n in line_counts.items():
                if ch not in accepted_bases:
                    counts["unknown"][ch] = (
                        counts["unknown"].get(ch, 0) + n
                    )
    return counts

def count_header_symbols(fasta_path: Path) -> dict[str, int]:
    counts = {}

    with open(fasta_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith(">"):
                for ch in line.strip():
                    counts[ch] = counts.get(ch, 0) + 1

    return counts

def read_fasta_description(fasta_path: Path) -> str:
    """
    Llegeix la primera capçalera FASTA i retorna la descripció,
    és a dir, tot el que ve després del primer identificador.
    
    Exemple:
    >U00096.3 Escherichia coli str. K-12 substr. MG1655, complete genome
    
    retorna:
    Escherichia coli str. K-12 substr. MG1655, complete genome
    """
    with open(fasta_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith(">"):
                header = line[1:].strip()
                parts = header.split(maxsplit=1)

                if len(parts) == 2:
                    return parts[1]
                else:
                    return parts[0]

    return fasta_path.stem.replace("_", " ")

def delete_fasta_header(fasta_path: Path, output_path: Path) -> None:
    """
    Crea una nova versió del fitxer FASTA sense les línies de capçalera (les que comencen amb '>').
    """
    with open(fasta_path, "r", encoding="utf-8", errors="ignore") as infile, \
         open(output_path, "w", encoding="utf-8") as outfile:
        for line in infile:
            if not line.startswith(">"):
                outfile.write(line)

