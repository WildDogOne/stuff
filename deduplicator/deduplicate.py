import os
import hashlib
import argparse
import sys
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def sha256_checksum(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(8192)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


def deduplicate_files(directory, delete_files):
    file_hashes = {}
    deduplicated_count = 0
    total_files = sum([len(files) for _, _, files in os.walk(directory)])

    logger.info("Starting deduplication process...")

    with tqdm(total=total_files, unit=" files", desc="Deduplicating") as pbar:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_hash = sha256_checksum(file_path)

                if file_hash not in file_hashes:
                    file_hashes[file_hash] = file_path
                else:
                    logger.info(f"\nDuplicate found: {file_path}")
                    logger.info(f"Original file: {file_hashes[file_hash]}")
                    if delete_files:
                        os.remove(file_path)
                        logger.info(f"Removed duplicate file: {file_path}")
                        deduplicated_count += 1
                    else:
                        logger.info(f"Dry run: Not removing duplicate file: {file_path}")
                        deduplicated_count += 1
                pbar.update(1)

    logger.info(
        f"\nDeduplication complete. {deduplicated_count} duplicate files {'deleted' if delete_files else 'identified'}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deduplicate files based on SHA256 checksum")
    parser.add_argument("directory", help="Directory to deduplicate")
    parser.add_argument("--delete", action="store_true", help="Delete duplicate files (default is dry run)")

    args = parser.parse_args()

    if not os.path.exists(args.directory):
        logger.error(f"Directory '{args.directory}' does not exist.")
        sys.exit(1)

    deduplicate_files(args.directory, args.delete)
