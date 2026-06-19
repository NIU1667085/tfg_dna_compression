#!/usr/bin/env python3
# ./plot_scatter_by_label.py -x compress_seconds -y bits_per_base_seq --output-dir /home/helen/genomic_benchmark/proves/plots/time_bpb /home/helen/genomic_benchmark/proves/comparative_results_updated.csv

import argparse
import re
from pathlib import Path
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt

ALGOS = ["gzip", "bzip2", "genozip", "mfcompress",  "naf", "geco3", "paq8l"]
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
GENERIC_OUTPUT_DIR = Path.home() / "genomic_benchmark" / "plots" 

options = {
    "compress_seconds": "Temps de compressió (s)", 
    "decompress_seconds": "Temps de descompressió (s)", 
    "bits_per_base_seq": "Compressió obtinguda (bpb)",
    "compress_MBps": "Velocitat de compressió (MB/s)",
    "decompress_MBps": "Velocitat de descompressió (MB/s)",
    "compression_percent": "Percentatge de compressió (%)",
    "compression_ratio": "Raó de compressió",
    "original_size_bytes": "Mida original (bytes)",
    }

DEFAULT_PLOTS = [
    {
        "x": "compress_seconds",
        "y": "bits_per_base_seq",
        "output_dir": "time_bpb",
    },
    {
        "x": "compress_seconds",
        "y": "decompress_seconds",
        "output_dir": "time",
    },
    {
        "x": "compression_percent",
        "y": "bits_per_base_seq",
        "output_dir": "bpb",
    },
]


def clean_filename(name: str) -> str:
    """
    Converteix un nom de label en un nom de fitxer segur.
    """
    return (
        name.lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
        .replace(",", "")
        .replace("(", "")
        .replace(")", "")
    )

def clean_title(label: str) -> str:
    return re.sub(r"\s*\([^)]*\)", "", label)

def plot_scatter_by_label(df: pd.DataFrame, output_dir: Path, x_key: str, y_key: str):
    output_dir.mkdir(parents=True, exist_ok=True)

    labels = sorted(df["dataset_label"].dropna().unique())
    title = f"{clean_title(options[x_key])} vs {clean_title(options[y_key])}"

    for label in labels:
        subdf = df[df["dataset_label"] == label].copy()

        if subdf.empty:
            continue

        plt.figure(figsize=(10, 6))

        for algo in sorted(subdf["algorithm"].dropna().unique()):
            algo_df = subdf[subdf["algorithm"] == algo]
            
            
            plt.scatter(
                algo_df[x_key],
                algo_df[y_key],
                label=algo,
                alpha=0.8,
                color = colors[ALGOS.index(algo) % len(colors)]
            )
            
        plt.xlabel(options[x_key])
        plt.ylabel(options[y_key])
        plt.title(f"{title} - {label}")

        if y_key == "bits_per_base_seq":
            mean_entropy = subdf["entropy_acgt_bpb"].mean()
            min_entropy = subdf["entropy_acgt_bpb"].min()
            max_entropy = subdf["entropy_acgt_bpb"].max()
            plt.axhline(mean_entropy, color="black", linestyle="-", label=f"H0 mitjana: {mean_entropy:.2f} bpb")
            plt.axhline(min_entropy, color="grey", linestyle=":", label=f"H0 mínima: {min_entropy:.2f} bpb")
            plt.axhline(max_entropy, color="grey", linestyle=":", label=f"H0 màxima: {max_entropy:.2f} bpb")

        # Fer que els eixos comencin sempre a 0
        # plt.xlim(left=0)
        # plt.ylim(bottom=0)

        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()

        out_path = output_dir / f"scatter-{x_key}-{y_key}-{label}.png"
        plt.savefig(out_path, dpi=300)
        plt.close()

        print(f"[OK] Plot saved in: {out_path}")

def parse_args():
    parser = argparse.ArgumentParser(
        description="Genera scatter plots a partir d'un CSV."
    )

    parser.add_argument(
        "csv_path",
        type=Path,
        help="Camí al fitxer CSV."
    )

    parser.add_argument(
        "--x-label",
        "-x",
        choices=options.keys(),
        help="Variable per a l'eix X."
    )

    parser.add_argument(
        "--y-label",
        "-y",
        choices=options.keys(),
        help="Variable per a l'eix Y."
    )

    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=None,
        help="Directori de sortida."
    )

    return parser.parse_args()

def prepare_dataframe(df, x_var, y_var, algos = ALGOS):

    required_columns = {
        "dataset_id",
        "dataset_label",
        "algorithm",
        "status",
        "entropy_acgt_bpb",
        x_var,
        y_var,
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Falten columnes al CSV: {sorted(missing)}"
        )

    df = df.copy()

    df[x_var] = pd.to_numeric(df[x_var], errors="coerce")
    df[y_var] = pd.to_numeric(df[y_var], errors="coerce")

    df = df.dropna(subset=[x_var, y_var])

    df = df[df["status"].isin(["ok", "ok_std"])]
    df = df[df["algorithm"].isin(algos)]

    return df

def generate_default_plots(df):
    
    print("[INFO] Generant plots per defecte...")
        
    algos_mod = ALGOS.copy()
    output_dir = GENERIC_OUTPUT_DIR / "all"
    
    for _ in range(2):

        for plot in DEFAULT_PLOTS:

            x_var = plot["x"]
            y_var = plot["y"]
            output_dir_mod = output_dir / plot["output_dir"]

            print(
                f"[INFO] {options[y_var]} vs {options[x_var]}"
            )

            df_plot = prepare_dataframe(
                df,
                x_var,
                y_var,
                algos = algos_mod
            )

            if df_plot.empty:
                print(
                    f"[WARNING] No hi ha dades vàlides per "
                    f"{x_var} vs {y_var}"
                )
                continue

            plot_scatter_by_label(
                df_plot,
                output_dir_mod,
                x_var,
                y_var,
            )
        
        algos_mod = ["gzip", "bzip2", "genozip", "mfcompress",  "naf"]
        output_dir = GENERIC_OUTPUT_DIR / "without_geco3_paq8l"

def main():

    args = parse_args()
    csv_path = args.csv_path
    df = pd.read_csv(csv_path)

    if args.x_label is None and args.y_label is None:
        generate_default_plots(df, csv_path)
        return

    output_dir = args.output_dir if args.output_dir else GENERIC_OUTPUT_DIR
    x_var = args.x_label
    y_var = args.y_label

    df = pd.read_csv(csv_path)

    required_columns = {
        "dataset_id",
        "dataset_label",
        "algorithm",
        "status",
        "entropy_acgt_bpb",
        x_var,
        y_var
    }

    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Falten columnes al CSV: {missing}")

    # Convertir columnes numèriques per evitar errors si hi ha valors buits
    df[x_var] = pd.to_numeric(df[x_var], errors="coerce")
    df[y_var] = pd.to_numeric(df[y_var], errors="coerce")

    # Filtrar files sense valors útils
    df = df.dropna(subset=[x_var, y_var])
    df = df[df["status"].isin(["ok", "ok_std"])]

    # Filtrar només els algorismes d'interès
    df = df[df["algorithm"].isin(ALGOS)]

    df = df[df["status"].isin(["ok", "ok_noN"])]

    if df.empty:
        print("[WARNING] No hi ha dades vàlides per fer plots.")
        return

    plot_scatter_by_label(
        df=df,
        output_dir=output_dir,
        x_key=x_var,
        y_key=y_var,
    )


if __name__ == "__main__":
    main()