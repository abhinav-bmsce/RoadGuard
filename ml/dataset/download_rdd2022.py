"""
RoadGuard - RDD2022 Dataset Downloader
Official Source: Crowdsensing-based Road Damage Detection Challenge (CRDDC 2022)
Hosted by Sekilab / Maeda et al., University of Tokyo
"""

import os
import sys
import argparse
import urllib.request
import zipfile
import tarfile
import shutil
from pathlib import Path

# Official RDD2022 dataset URLs / mirrors
# The complete CRDDC'2022 dataset consists of multi-country subsets (Japan, India, Czech, Norway, United States, China)
RDD2022_URLS = {
    "Japan": "https://bigdata-cup.s3.ap-northeast-1.amazonaws.com/2022/CRDDC2022/RDD2022_Japan.tar.gz",
    "India": "https://bigdata-cup.s3.ap-northeast-1.amazonaws.com/2022/CRDDC2022/RDD2022_India.tar.gz",
    "Czech": "https://bigdata-cup.s3.ap-northeast-1.amazonaws.com/2022/CRDDC2022/RDD2022_Czech.tar.gz",
}

SAMPLE_SUBSET_URL = "https://github.com/sekilab/RoadDamageDetector/raw/master/sample_data.zip"


def download_progress_hook(count, block_size, total_size):
    percent = int(count * block_size * 100 / (total_size + 1e-5))
    sys.stdout.write(f"\rDownloading: {percent}% [{count * block_size / (1024*1024):.1f} MB / {total_size / (1024*1024):.1f} MB]")
    sys.stdout.flush()


def download_dataset(country: str, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    if country not in RDD2022_URLS:
        print(f"Error: Unknown country '{country}'. Available: {list(RDD2022_URLS.keys())}")
        return

    url = RDD2022_URLS[country]
    archive_path = output_dir / f"RDD2022_{country}.tar.gz"

    print(f"Downloading RDD2022 {country} subset from official repository...")
    print(f"URL: {url}")
    print(f"Destination: {archive_path}")

    try:
        urllib.request.urlretrieve(url, archive_path, reporthook=download_progress_hook)
        print("\nDownload finished. Extracting archive...")
        if str(archive_path).endswith(".tar.gz") or str(archive_path).endswith(".tgz"):
            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extractall(path=output_dir)
        elif str(archive_path).endswith(".zip"):
            with zipfile.ZipFile(archive_path, "r") as z:
                z.extractall(path=output_dir)
        print(f"Successfully extracted to: {output_dir}")
    except Exception as e:
        print(f"\nDownload/Extraction failed: {e}")
        print("Note: In Google Colab or environments with curl/wget, you can also run:")
        print(f"  wget {url} -O {archive_path}")
        print(f"  tar -xzf {archive_path} -C {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download RDD2022 Dataset Subsets")
    parser.add_argument("--country", type=str, default="Japan", choices=["Japan", "India", "Czech", "All"], help="Country subset to download")
    parser.add_argument("--output", type=str, default="./ml/dataset/raw", help="Target output directory")
    args = parser.parse_args()

    out_path = Path(args.output).resolve()
    if args.country == "All":
        for c in ["Japan", "India", "Czech"]:
            download_dataset(c, out_path)
    else:
        download_dataset(args.country, out_path)

