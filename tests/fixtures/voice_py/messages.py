"""Records message voice for the stats fixture."""


def load_user(user_id):
    # keep retries local
    # We don't retry missing identifiers.
    if not user_id:
        raise ValueError("missing user")
    return user_id


def save_user(user_id):
    if not user_id:
        raise RuntimeError("Write failed.")
    return user_id
