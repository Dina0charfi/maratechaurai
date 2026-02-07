from pathlib import Path
from random import choice

import torch

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = Path(__file__).resolve().parent / "dataset"
MAPPING_PATHS = [
	REPO_ROOT / "sign_language_model.ptl",
]


def _load_mapping_from_file(path: Path):
	if not path.exists():
		return None
	try:
		data = torch.load(path, map_location="cpu")
	except Exception:
		return None
	if not isinstance(data, dict):
		return None

	normalized = {}
	for word, images in data.items():
		if not isinstance(word, str):
			continue
		if isinstance(images, (list, tuple)) and images:
			normalized[word.lower()] = [str(img) for img in images]

	return normalized or None


def _scan_dataset(dataset_dir: Path):
	mapping = {}
	if not dataset_dir.exists():
		return mapping

	for category in dataset_dir.iterdir():
		if not category.is_dir():
			continue
		for word_dir in category.iterdir():
			if not word_dir.is_dir():
				continue
			images = [str(img) for img in word_dir.glob("*.jpg")]
			if images:
				mapping[word_dir.name.lower()] = images

	return mapping


def _load_word_to_images():
	for path in MAPPING_PATHS:
		mapping = _load_mapping_from_file(path)
		if mapping:
			return mapping
	return _scan_dataset(DATASET_DIR)


word_to_images = _load_word_to_images()


def get_sign_for_word(word: str):
	if not word:
		return None
	images = word_to_images.get(word.lower())
	if images:
		return choice(images)
	return None

