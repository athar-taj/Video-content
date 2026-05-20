import hashlib
from pathlib import Path

class AudioChecksum:
    """
    Utility to generate and verify file checksums for audio integrity.
    """
    
    @staticmethod
    def generate_sha256(file_path: Path) -> str:
        """Generates SHA256 hash of a file."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read in chunks to avoid memory issues with large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def verify_checksum(file_path: Path, expected_checksum: str) -> bool:
        """Verifies if the file's checksum matches the expected value."""
        actual_checksum = AudioChecksum.generate_sha256(file_path)
        return actual_checksum == expected_checksum
