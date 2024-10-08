from datasets import load_dataset
import random
import numpy as np
import logging


def _get_wikitext2(split):
    assert split in [
        "train",
        "validation",
        "test",
    ], f"Unknown split {split} for wikitext2"

    data = load_dataset(
        "wikitext", "wikitext-2-raw-v1", split=split, trust_remote_code=True
    )
    return data["text"]


def _get_ptb(split, slice_unk=True):
    assert split in ["train", "validation", "test"], f"Unknown split {split} for ptb"

    data = load_dataset(
        "ptb_text_only", "penn_treebank", split=split, trust_remote_code=True
    )
    data_list = data["sentence"]

    if slice_unk:
        data_list = [s.replace("<unk>", "< u n k >") for s in data_list]

    return data_list


def _get_c4(split):
    assert split in ["train", "validation"], f"Unknown split {split} for c4"

    if split == "train":
        data = load_dataset(
            "allenai/c4",
            data_files={"train": "en/c4-train.00000-of-01024.json.gz"},
            split="train",
            trust_remote_code=True,
        )
    else:
        assert split == "validation"
        data = load_dataset(
            "allenai/c4",
            data_files={"validation": "en/c4-validation.00000-of-00008.json.gz"},
            split="validation",
            trust_remote_code=True,
        )

    return data["text"]


def _get_pileval(split):
    if split != "validation":
        logging.warning(
            f"Pileval only has a validation split, but got split={split}. Using validation split."
        )
    data = load_dataset(
        "mit-han-lab/pile-val-backup", split="validation", trust_remote_code=True
    )

    return data["text"]


def _sample_and_tokenize(texts, tokenizer, seq_len, num_samples, seed=None):
    assert num_samples <= len(
        texts
    ), f"num_samples({num_samples}) should be less than or equal to the number of texts({len(texts)})"

    # this works for None too, effectively setting random seeds
    random.seed(seed)
    np.random.seed(seed)

    selected_indices = set()

    samples = []
    while len(samples) < num_samples:
        idx = random.randint(0, len(texts) - 1)
        if idx in selected_indices:  # we don't want to sample the same text twice
            continue
        text = texts[idx]

        tokens = tokenizer(text, return_tensors="pt")["input_ids"][0]
        if len(tokens) < seq_len:  # if the text is too short, we skip it
            continue

        tokens = tokens[:seq_len]

        selected_indices.add(idx)
        samples.append(tokens)

    return samples


def _get_dataset(dataset_name, split):
    if dataset_name == "wikitext2":
        return _get_wikitext2(split)
    elif dataset_name == "ptb":
        return _get_ptb(split)
    elif dataset_name == "c4":
        return _get_c4(split)
    elif dataset_name == "pileval":
        return _get_pileval(split)
    else:
        raise ValueError(f"Unknown dataset {dataset_name}")


def get_tokens(dataset_name, split, tokenizer, seq_len, num_samples, seed=None):
    logging.info(f"Fetching dataset: {dataset_name}")
    texts = _get_dataset(dataset_name, split)
    logging.info(
        f"Sampling {num_samples} samples of length {seq_len} from {dataset_name}..."
    )
    return _sample_and_tokenize(texts, tokenizer, seq_len, num_samples, seed)
