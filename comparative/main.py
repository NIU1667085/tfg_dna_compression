#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import argparse

from datasets import load_datasets
from algorithms import available_algorithms
from benchmark import benchmark_one
from utils import write_csv
from entities import BenchmarkPaths

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "chromosome"
DATA_NO_HEADERS_DIR = ROOT / "data_no_headers"
RESULTS_DIR = ROOT / "results"

TIMESTAMP = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
RUN_DIR = RESULTS_DIR / TIMESTAMP

paths = BenchmarkPaths(
    compressed_dir=RUN_DIR / "compressed",
    decompressed_dir=RUN_DIR / "decompressed",
    logs_dir=RUN_DIR / "logs",
    tmp_dir=RUN_DIR / "tmp",
)

for d in [
    paths.compressed_dir,
    paths.decompressed_dir,
    paths.logs_dir,
    paths.tmp_dir,
    RUN_DIR / "tables",
    RUN_DIR / "plots",
]:
    d.mkdir(parents=True, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Run benchmarking")
    parser.add_argument("num_algorithms", type=int)
    args = parser.parse_args()

    datasets = load_datasets(DATA_DIR)
    algos = available_algorithms()

    if args.num_algorithms != len(algos):
        print(f"Requested {args.num_algorithms} algorithms")
        print(f"Found {len(algos)} algorithms: {[a.name for a in algos]}")
        print("Check your data directory and PATH for available algorithms.")
        return

    if not datasets:
        print(f"No FASTA files found in {DATA_DIR}")
        return
    if not algos:
        print("No algorithms found in PATH")
        return

    print(f"Using {len(datasets)} datasets, {len(algos)} algorithms")

    rows = []
    for x, ds in enumerate(datasets):
        for y, algo in enumerate(algos):
            
            # if ds.label == "chromosome" or (algo.name == "paq8l" and ds.label in ("chromosome", "genome")):
            #     print(f"[SKIP] {ds.dataset_id} / {algo.name} (too slow)")
            #     continue
            
            print(f"[RUN {x+1}.{y+1}] {ds.dataset_id} / {algo.name}")
            try:
                results = benchmark_one(ds, algo, paths)
                rows.append(results)
            except Exception as e:
                print(f"[ERROR] {ds.dataset_id} / {algo.name}: {e}")

    filename = f"comparative_results_{TIMESTAMP}.csv"
    
    out_csv = RUN_DIR / filename
    write_csv(rows, out_csv)
    print(f"Results written to {out_csv}")

if __name__ == "__main__":
    main()