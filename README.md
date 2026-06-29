# TFG — DNA Compression Benchmark

A comparative benchmarking framework for DNA sequence compression algorithms, developed as a Bachelor's thesis (TFG). The system evaluates 11 compression algorithms across 28 genomic datasets, measuring compression ratio, speed, memory usage, and information-theoretic limits.

---

## Project Structure

```
tfg_dna_compression/
├── comparative/               # Core benchmarking framework
│   ├── main.py               # Entry point
│   ├── algorithms.py         # Algorithm discovery and command templates
│   ├── benchmark.py          # Run compress/decompress, validate, measure
│   ├── datasets.py           # Dataset loading and base composition analysis
│   ├── entities.py           # Data classes: Dataset, Algorithm, ResultRow
│   ├── fasta_utils.py        # FASTA parsing utilities
│   ├── utils.py              # Entropy calculations, CSV output
│   ├── pre_post_process.py   # Strip/restore non-standard bases (for GeCo3)
│   ├── plot_scatter_by_label.py  # Scatter plot generation from results CSV
│   └── deepdna/   
│       ├── deepdna_main.ipynb      # Complete pipeline for DeepDNA compression and decompression
│       ├── deepdna_train.ipynb     # Script to train the DeepDNA model
│       └── train_data/             # Training sequences for DeepDNA
├── tools/
│   ├── bin/                  # Compiled binaries (MFCompress, GeCo3, etc.)
│   └── src/                  # Source trees for each compression tool
├── proves/                   # Jupyter notebooks for analysis and plots
├── comparative_results.csv   # Existing benchmark results 
├── download_datasets.sh      # Download genomic datasets from NCBI
└── requirements.txt          # Python dependencies
```

---

## Algorithms

Seven algorithms are compared in the main benchmark:

| Algorithm | Type | Notes |
|---|---|---|
| gzip | Generic baseline | Standard DEFLATE |
| bzip2 | Generic baseline | Block-sorting compressor |
| PAQ8L | Generic baseline | Context mixing, advanced probabilistic model |
| Genozip | Genomic specialized | VCF/FASTA-aware |
| MFCompress | Genomic specialized | Markov field model |
| NAF | Genomic specialized | zstd-based, FASTA/FASTQ |
| GeCo3 | Context mixing + NN | Neural network expert mixer; only works with ACGT |


**DeepDNA** is evaluated separately as a standalone end-to-end pipeline (see [DeepDNA](#deepdna)).

---

## Datasets

Downloaded from NCBI using `efetch`. Five categories:

| Category | Genomes | Example |
|---|---|---|
| Virus | 6 | SARS-CoV-2, HIV, PhiX174 |
| Bacteria | 6 | *E. coli*, *M. tuberculosis*, *S. aureus* |
| Mitochondria | 6 | Human mitochondrion + 5 *PV* sequences |
| Eukaryota chromosomes | 4 | *A. thaliana*, *S. cerevisiae* |
| *H. sapiens* chromosomes | 4 | chr21, chr22, chrX, chrY |

---

## Installation

### 1. Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Compression tool binaries

Each tool under `tools/src/` must be compiled separately following its own build instructions. Compiled binaries should be placed in `tools/bin/` and added to `PATH` before running the benchmark.

### 3. Download datasets

```bash
bash download_datasets.sh
```

Download FASTA files to `~/genomic_benchmark/data/`, organized by category.

---

## Usage

### Run the benchmark

First download the datasets, then run the comparison:

```bash
bash download_datasets.sh
```

```bash
cd comparative
python main.py <num_algorithms>
```

`<num_algorithms>` must match the number of algorithms that `algorithms.py` finds available in `PATH` (up to 7). The script checks this at startup and will fail early if the count doesn't match. Results are written to `./results/<TIMESTAMP>/comparative_results_<TIMESTAMP>.csv`.

### Generate scatter plots

```bash
python comparative/plot_scatter_by_label.py <path_to_csv> \
    -x <x_metric> -y <y_metric> -o <output_dir>
```

Example:

```bash
python comparative/plot_scatter_by_label.py comparative_results.csv \
    -x compress_seconds -y bits_per_base_seq -o plots/
```

### Explore results interactively

Notebooks in `proves/` let you work with the results CSV and dataset statistics dynamically:

- `d_calcul_freqs.ipynb` — base frequency distributions
- `d_entropies_dades.ipynb` — Shannon entropy analysis
- `d_resum_mida.ipynb` — dataset size summary
- `r_diff_temps_c_d.ipynb` — compression vs decompression timing
- `r_join_csv.ipynb` — merge result CSVs
- `r_join_entropies.ipynb` — aggregate entropy data
- `r_performance_2algos.ipynb` — head-to-head algorithm comparison
- `r_plots.ipynb` — full result visualization plots

---

## Metrics

Each benchmark run records, some of them:

| Metric | Description |
|---|---|
| `compression_ratio` | Original size / compressed size |
| `compression_percent` | 1 - 1/ `compression_ratio` |
| `bits_per_base_seq` | Compressed bits per nucleotide (sequence only) |
| `compress_seconds` | Compression time |
| `decompress_seconds` | Decompression time |
| `entropy_acgt` | Shannon entropy over A/C/G/T |
| `entropy_acgtn` | Shannon entropy over A/C/G/T/N |
| `status` | Validation result (`ok`, `ok_seq`, `ok_std`, `compress_error`, `mismatch`) |

Validation checks bitwise identity between the original and decompressed file. Algorithms (like GeCo3) that don't work with non-standard bases (N, ambiguous IUPAC codes) or FASTA headers should be run through `pre_post_process.py`, which strips and restores those positions losslessly.

---

## GeCo3 pre/post-processing

GeCo3 only accepts plain ACGT sequences — it ignores FASTA headers and does not handle non-ACGT characters. `comparative/pre_post_process.py` handles this transparently:

1. **Pre-processing** — strips headers and records the positions of any non-ACGT characters (N, ambiguous IUPAC codes) as JSON metadata.
2. **Post-processing** — restores headers and non-ACGT positions after decompression, ensuring a complete lossless process.

This step should be run as part of the benchmark for the GeCo3 algorithm.

---

## DeepDNA

DeepDNA is a CNN+LSTM hybrid evaluated as a standalone pipeline, separate from the main 7-algorithm comparison.

| Notebook | Purpose |
|---|---|
| `comparative/deepdna/deepdna_main.ipynb` | End-to-end compression and decompression pipeline |
| `comparative/deepdna/deepdna_train.ipynb` | Retrain the model on new data |

Training data (human mitochondrial sequences from MITOMAP) is in `comparative/deepdna/train_data/`.

---

## Results

A pre-computed results file is included at [comparative_results.csv](comparative_results.csv) (188 benchmark rows across 8 algorithms and 26 datasets).
