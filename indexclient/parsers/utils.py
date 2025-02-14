import logging


def remove_extra_hashes(hash_dict, hash_set):
    """Remove extra hashes from set, log errors"""
    logging.error("multiple incompatible hashes specified")

    for hash_item in hash_dict.items():
        hash_set.remove(hash_item)

    for hash_item, _ in hash_set:
        logging.error(f"multiple values specified for {hash_item}")

    return hash_set
