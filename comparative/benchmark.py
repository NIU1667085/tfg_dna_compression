#!/usr/bin/env python3

import shlex
import shutil
import subprocess
import time
from pathlib import Path

from entities import Dataset, Algorithm, ResultRow, BenchmarkPaths
from utils import file_size, sha256_file, extract_sequence, remove_unknown, mbps


def run_command(command: str, stderr_path: Path) -> tuple[int, float]:
    start = time.perf_counter()

    with open(stderr_path, "a", encoding="utf-8") as errf:
        errf.write(f"\n$$ {command}\n")
        proc = subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=errf)

    total_time = time.perf_counter() - start
    return proc.returncode, total_time


def build_compress_command(algo: Algorithm, input_path: Path, compressed_path: Path, tmp_dir: Path = None) -> str:
    if algo.name == "naf":
        tmp_dir.mkdir(parents=True, exist_ok=True)
        return algo.compress_cmd.format(
            input=shlex.quote(str(input_path)),
            output=shlex.quote(str(compressed_path)),
            temp_dir=shlex.quote(str(tmp_dir)),
        )

    return algo.compress_cmd.format(
        input=shlex.quote(str(input_path)),
        output=shlex.quote(str(compressed_path)),
    )


def build_decompress_command(algo: Algorithm, compressed_path: Path, decompressed_path: Path) -> str:
    if algo.name == "paq8l":
        return algo.decompress_cmd.format(
            input=shlex.quote(str(compressed_path)),
            output_dir=shlex.quote(str(decompressed_path.parent)),
        )

    return algo.decompress_cmd.format(
        input=shlex.quote(str(compressed_path)),
        output=shlex.quote(str(decompressed_path)),
    )


def move_compressed_file_if_needed(algo: Algorithm, input_path: Path, compressed_path: Path) -> None:
    """
    Alguns algorismes no deixen escollir exactament el fitxer de sortida.
    Aquesta funció mou el fitxer produït cap al path estàndard del benchmark.

    Fix específic per a PAQ8L i GECO3, que no permeten especificar el nom del fitxer de sortida i el deixen al mateix directori que l'input
    """
    if algo.name == "paq8l":
        produced_file = input_path.with_suffix(input_path.suffix + ".paq8l")
        if produced_file.exists():
            shutil.move(produced_file, compressed_path)

    elif algo.name == "geco3":
        produced_file = input_path.with_suffix(input_path.suffix + ".co")
        if produced_file.exists():
            shutil.move(produced_file, compressed_path)


def move_decompressed_file_if_needed(algo: Algorithm, input_path: Path, compressed_path: Path, decompressed_path: Path) -> None:
    if algo.name == "paq8l":
        produced_file = decompressed_path.parent / input_path.name
        if produced_file.exists() and produced_file != decompressed_path:
            shutil.move(produced_file, decompressed_path)

    elif algo.name == "geco3":
        produced_file = compressed_path.with_suffix(".de")
        if produced_file.exists():
            shutil.move(produced_file, decompressed_path)


def validate_decompression(input_path: Path, decompressed_path: Path, num_no_std: int) -> tuple[bool, bool, bool]:
    """
    Retorna:
    - bitwise_ok: el fitxer és idèntic byte a byte
    - sequence_ok_all: la seqüència FASTA és igual
    - sequence_ok_std: la seqüència és igual ignorant tots els no ACGT
    """
    if not decompressed_path.exists():
        print("Output file does not exist")
        return False, False, False

    bitwise_ok = sha256_file(input_path) == sha256_file(decompressed_path)

    try:
        seq_in = extract_sequence(input_path)
        seq_out = extract_sequence(decompressed_path)

        sequence_ok_all = seq_in == seq_out
        sequence_ok_std = False

        if not sequence_ok_all and num_no_std > 0:
            sequence_ok_std = remove_unknown(seq_in) == remove_unknown(seq_out)
        elif sequence_ok_all: 
            sequence_ok_std = True

        return bitwise_ok, sequence_ok_all, sequence_ok_std

    except Exception:
        return bitwise_ok, False, False

def benchmark_one(ds: Dataset, algo: Algorithm, paths: BenchmarkPaths) -> ResultRow:
    input_path = ds.fasta_path
    original_size = file_size(input_path)

    num_bases_seq = ds.num_bases_seq
    num_A = ds.base_counts.get("A", 0)
    num_C = ds.base_counts.get("C", 0)
    num_G = ds.base_counts.get("G", 0)
    num_T = ds.base_counts.get("T", 0)
    num_N = ds.base_counts.get("N", 0)
    num_unknown = sum(ds.base_counts.get("unknown", {}).values())

    # Entropia teòrica d'ordre 0 de la seqüència.
    # H0(A,C,G,T,N): útil si vols considerar N com un símbol més.
    # H0(A,C,G,T): útil si vols analitzar només les bases conegudes.
    size_header = ds.size_header
    entropy_acgtn = ds.entropy_acgtn_bits_per_base
    entropy_acgt = ds.entropy_acgt_bits_per_base
    entropy_seq = ds.entropy_seq_all_bits_per_base
    entropy_all = ds.entropy_seq_all_headers_bits_per_base

    compressed_path = paths.compressed_dir /ds.dataset_id / algo.name / f"{input_path.name}{algo.compressed_ext}"
    decompressed_path = paths.decompressed_dir / ds.dataset_id / algo.name / input_path.name
    stderr_path = paths.logs_dir / f"{ds.dataset_id}.{algo.name}.stderr.txt"

    for p in [compressed_path, decompressed_path, stderr_path]:
        p.parent.mkdir(parents=True, exist_ok=True)

    if compressed_path.exists():
        compressed_path.unlink()

    if decompressed_path.exists():
        decompressed_path.unlink()

    if stderr_path.exists():
        stderr_path.unlink()

    compress_cmd = build_compress_command(
        algo=algo,
        input_path=input_path,
        compressed_path=compressed_path,
        tmp_dir=paths.tmp_dir,
    )

    c_code, compress_seconds = run_command(
        compress_cmd,
        stderr_path,
    )

    move_compressed_file_if_needed(
        algo=algo,
        input_path=input_path,
        compressed_path=compressed_path,
    )

    compressed_size = file_size(compressed_path) if compressed_path.exists() else -1

    d_code = -1
    decompress_seconds = 0.0

    if compressed_path.exists() and c_code == 0:
        decompress_cmd = build_decompress_command(
            algo=algo,
            compressed_path=compressed_path,
            decompressed_path=decompressed_path,
        )

        d_code, decompress_seconds = run_command(
            decompress_cmd,
            stderr_path,
        )

        move_decompressed_file_if_needed(
            algo=algo,
            input_path=input_path,
            compressed_path=compressed_path,
            decompressed_path=decompressed_path,
        )

    if algo.name == "naf" and paths.tmp_dir.exists():
        shutil.rmtree(paths.tmp_dir)

    bitwise_ok, sequence_ok_all, sequence_ok_std = validate_decompression(
        input_path=input_path,
        decompressed_path=decompressed_path,
        num_no_std=num_N + num_unknown,
    )

    ratio = (original_size / compressed_size) if compressed_size > 0 else None
    percent = (100.0 * (1.0 - compressed_size / original_size)) if compressed_size > 0 else None
    
    # Incloent headers (fitxer complet)
    bits_per_base_total = (
        (compressed_size * 8.0) / original_size
    ) if compressed_size > 0 and original_size > 0 else None

    # Només seqüència
    bits_per_base_seq = (
        (compressed_size * 8.0) / num_bases_seq
    ) if compressed_size > 0 and num_bases_seq > 0 else None

    status = "ok" if (c_code == 0 and d_code == 0 and bitwise_ok) else (
        "ok_seq" if (c_code == 0 and d_code == 0 and sequence_ok_all) else (
            "ok_std" if (c_code == 0 and d_code == 0 and sequence_ok_std) else (
                "compress_error" if c_code != 0 else (
                    "decompress_error" if d_code != 0 else (
                        "mismatch"
                    )
                )
            )
        )
    )

    return ResultRow(
        dataset_id=ds.dataset_id,
        dataset_label=ds.label,
        algorithm=algo.name,
        original_size_bytes=original_size,
        compressed_size_bytes=compressed_size,
        compression_ratio=ratio,
        compression_percent=percent,
        bits_per_base_seq=bits_per_base_seq,
        size_header=size_header,
        entropy_acgtn_bpb=entropy_acgtn,
        entropy_acgt_bpb=entropy_acgt,
        entropy_seq_bpb=entropy_seq,
        entropy_all_bpb=entropy_all,
        compress_seconds=compress_seconds,
        decompress_seconds=decompress_seconds,
        compress_MBps=mbps(original_size, compress_seconds),
        decompress_MBps=mbps(original_size, decompress_seconds),
        bitwise_ok=bitwise_ok,
        sequence_ok_all=sequence_ok_all,
        sequence_ok_std=sequence_ok_std,
        compress_exit_code=c_code,
        decompress_exit_code=d_code,
        stderr_log=str(stderr_path),
        status=status,
        num_bases_seq=num_bases_seq,
        num_A=num_A,
        num_C=num_C,
        num_G=num_G,
        num_T=num_T,
        num_N=num_N,
        num_unknown=num_unknown,
    )