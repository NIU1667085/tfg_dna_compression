#!/usr/bin/env python3
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Dataset:
    dataset_id: str # num o codi curt
    label: str # categoria
    description: str
    fasta_path: Path 
    size_bytes: int
    num_bases_std: int # només A,C,G,T
    num_bases_seq: int # A,C,G,T,N i unknown
    base_counts: dict[str, int] # counts A,C,G,T,N i unknown
    size_header: float # quants caracters te el header
    header_counts: dict[str, int] # counts de caracters del header
    entropy_acgtn_bits_per_base: float | None # Entropia H0 sobre A,C,G,T,N
    entropy_acgt_bits_per_base: float | None # Entropia H0 sobre A,C,G,T ignorant N
    entropy_seq_all_bits_per_base: float | None # Entropia H0 sobre la seqüència completa
    entropy_seq_all_headers_bits_per_base: float | None # Entropia H0 sobre la seqüència completa i els headers
    contains_unknown: bool = False

@dataclass
class Algorithm:
    name: str
    compress_cmd: str
    decompress_cmd: str
    compressed_ext: str

@dataclass
class ResultRow:
    dataset_id: str
    dataset_label: str
    algorithm: str
    original_size_bytes: int
    compressed_size_bytes: int
    compression_ratio: float
    compression_percent: float
    bits_per_base_seq: float # eficiència sobre ADN pur (només seqüència)
    size_header: float 
    entropy_acgtn_bpb: float | None # Entropia H0 sobre A,C,G,T,N
    entropy_acgt_bpb: float | None # Entropia H0 sobre A,C,G,T ignorant N
    entropy_seq_bpb: float | None # Entropia H0 sobre la seqüència completa
    entropy_all_bpb: float | None # Entropia H0 sobre la seqüència completa i els headers
    compress_seconds: float
    decompress_seconds: float
    compress_MBps: float
    decompress_MBps: float
    bitwise_ok: bool
    sequence_ok_all: bool
    sequence_ok_std: bool
    compress_exit_code: int
    decompress_exit_code: int
    stderr_log: str
    status: str
    num_bases_seq: int
    num_A: int
    num_C: int
    num_G: int
    num_T: int
    num_N: int = 0
    num_unknown: int = 0

@dataclass
class BenchmarkPaths:
    compressed_dir: Path
    decompressed_dir: Path
    logs_dir: Path
    tmp_dir: Path