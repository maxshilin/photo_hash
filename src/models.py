from dataclasses import dataclass
from typing import Dict, List


@dataclass
class HashResult:
    path: str
    image_hash: str


@dataclass
class ImageProcessorResult:
    elapsed_seconds: float
    num_copies: int
    num_photos: int
    source_dir: str
    hash_dict: Dict[str, List[str]]
