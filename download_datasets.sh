#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTDIR="$SCRIPT_DIR/data2/"
mkdir -p "$OUTDIR"

download_fasta () {
    local id="$1"
    local accession="$2"
    local label="$3"

    echo "[DOWNLOAD] $id ($accession)"
    local outdir="$OUTDIR"/"$label"
    mkdir -p "$outdir"
    efetch -db nucleotide -id "$accession" -format fasta > "$outdir/${id}.fasta"
    

    if [[ ! -s "$outdir/${id}.fasta" ]]; then
        echo "[ERROR] Empty file for $id"
        exit 1
    fi

    echo "[OK] $outdir/${id}.fasta"
}

fetch_fasta () {
    local DIR="${1:-}"
    local OUT="${2:-all_files.fa}"

    if [[ ! -d "$DIR" ]]; then
        echo "[ERROR ALL] '$DIR' is not a valid folder." >&2
        exit 1
    fi

    : > "$OUT"

    local count=0

    while IFS= read -r -d '' file; do
        count=$((count + 1))
        echo "[JOIN] $file"

        cat "$file" >> "$OUT"
        echo >> "$OUT"
    done < <(
        find "$DIR" -maxdepth 1 -type f \( \
            -name "*.fa" -o -name "*.fasta" -o -name "*.fna" \
        \) -print0 | sort -z
    )

    if [[ "$count" -eq 0 ]]; then
        echo "[ERROR ALL]: there's no FASTA files in '$DIR'." >&2
        rm -f "$OUT"
        exit 1
    fi

    echo "[ALL OK]: $count FASTA files have been joined into '$OUT'."
}

# -------------------------
# Virus
# -------------------------
download_fasta "phix174" "NC_001422.1" "virus"
download_fasta "hpv16" "NC_001526.4" "virus"
download_fasta "sars_cov_2" "NC_045512.2" "virus"
download_fasta "phage_lambda" "NC_001416.1" "virus"
download_fasta "hsv1" "NC_001806.2" "virus"
download_fasta "hiv" "NC_001802.1" "virus"
# fetch_fasta "$OUTDIR/virus" "$OUTDIR/virus/virus_all.fa"

# -------------------------
# Bacteria
# -------------------------
download_fasta "staphylococcus_aureus" "NC_007795.1" "bacteria"
download_fasta "bacillus_subtilis" "NC_000964.3" "bacteria"
download_fasta "mycobacterium_tuberculosis" "NC_000962.3" "bacteria"
download_fasta "salmonella_typhimurium" "NC_003197.2" "bacteria"
download_fasta "pseudomonas_aeruginosa" "NC_002516.2" "bacteria"
download_fasta "escherichia_coli" "NC_000913.3" "bacteria"
# fetch_fasta "$OUTDIR/bacteria" "$OUTDIR/bacteria/bacteria_all.fa"

# -------------------------
# Mitocondria (Deep DNA)
# -------------------------
download_fasta "mitochondria" "NC_012920.1" "mitochondria"
download_fasta "PV559941.1" "PV559941.1" "mitochondria"
download_fasta "PV559966.1" "PV559966.1" "mitochondria"
download_fasta "PV559974.1" "PV559974.1" "mitochondria"
download_fasta "PV559982.1" "PV559982.1" "mitochondria"
download_fasta "PV560051.1" "PV560051.1" "mitochondria"
# fetch_fasta "$OUTDIR/mitochondria" "$OUTDIR/mitochondria/mitochondria_all.fa"

# -------------------------
# Homo sapiens
# -------------------------
# download_fasta "homo_sapiens_chr1" "NC_000001.11" "chromosome"
# download_fasta "homo_sapiens_chr4" "NC_000004.12" "chromosome"
download_fasta "homo_sapiens_chr21" "NC_000021.9" "chromosome"
download_fasta "homo_sapiens_chr22" "NC_000022.11" "chromosome"
download_fasta "homo_sapiens_chrX" "NC_000023.11" "chromosome"
download_fasta "homo_sapiens_chrY" "NC_000024.10" "chromosome"

# -------------------------
# Eucariota
# -------------------------
download_fasta "candidozma_auris" "NC_072812.1" "eucariota"
download_fasta "arabidopsis_thaliana" "NC_003070.9" "eucariota"
download_fasta "saccharomyces_cerevisiae" "NC_001133.9" "eucariota"
download_fasta "yarrowia_lipolytica" "NC_090774.1" "eucariota"
