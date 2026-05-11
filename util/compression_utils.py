import zlib
import gzip
import bz2
import lzma
import base64
from pathlib import Path


def zlib_compress(data: str | bytes, level: int = 6) -> bytes:
    if isinstance(data, str):
        data = data.encode()
    return zlib.compress(data, level)


def zlib_decompress(data: bytes) -> str:
    return zlib.decompress(data).decode()


def gzip_compress(data: str | bytes, level: int = 6) -> bytes:
    if isinstance(data, str):
        data = data.encode()
    return gzip.compress(data, compresslevel=level)


def gzip_decompress(data: bytes) -> str:
    return gzip.decompress(data).decode()


def bz2_compress(data: str | bytes, level: int = 9) -> bytes:
    if isinstance(data, str):
        data = data.encode()
    return bz2.compress(data, compresslevel=level)


def bz2_decompress(data: bytes) -> str:
    return bz2.decompress(data).decode()


def lzma_compress(data: str | bytes) -> bytes:
    if isinstance(data, str):
        data = data.encode()
    return lzma.compress(data)


def lzma_decompress(data: bytes) -> str:
    return lzma.decompress(data).decode()


def compress_file(src: str, dst: str, method: str = "gzip") -> int:
    data = Path(src).read_bytes()
    compressors = {
        "gzip": gzip.compress,
        "bz2": bz2.compress,
        "lzma": lzma.compress,
        "zlib": zlib.compress,
    }
    if method not in compressors:
        raise ValueError(f"Unknown method: {method!r}. Choose from {list(compressors)}")
    compressed = compressors[method](data)
    Path(dst).write_bytes(compressed)
    return len(compressed)


def compression_ratio(original: str | bytes, compressed: bytes) -> float:
    if isinstance(original, str):
        original = original.encode()
    return round(len(compressed) / len(original) * 100, 2)


if __name__ == "__main__":
    text = "Hello, World! " * 100

    zlib_data = zlib_compress(text)
    gzip_data = gzip_compress(text)
    bz2_data = bz2_compress(text)
    lzma_data = lzma_compress(text)

    original_size = len(text.encode())
    print(f"Original:  {original_size} bytes")
    print(f"zlib:      {len(zlib_data)} bytes ({compression_ratio(text, zlib_data)}%)")
    print(f"gzip:      {len(gzip_data)} bytes ({compression_ratio(text, gzip_data)}%)")
    print(f"bz2:       {len(bz2_data)} bytes ({compression_ratio(text, bz2_data)}%)")
    print(f"lzma:      {len(lzma_data)} bytes ({compression_ratio(text, lzma_data)}%)")

    print("\nround-trip zlib: ", zlib_decompress(zlib_data)[:20] + "...")
    print("round-trip gzip: ", gzip_decompress(gzip_data)[:20] + "...")
    print("round-trip bz2:  ", bz2_decompress(bz2_data)[:20] + "...")
    print("round-trip lzma: ", lzma_decompress(lzma_data)[:20] + "...")
