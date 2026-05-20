import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class DuplicateDetector:
    """
    Detects duplicate assets using SHA256 checksums.
    """
    
    @staticmethod
    def calculate_checksum(file_path: str) -> str:
        """
        Generates a SHA256 hash for a file.
        """
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read in 64kb chunks
                for byte_block in iter(lambda: f.read(65536), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Checksum calculation failed for {file_path}: {e}")
            raise

    def is_duplicate(self, checksum: str, existing_checksums: set[str]) -> bool:
        return checksum in existing_checksums
