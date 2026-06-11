"""Example service module for codedna stats tests."""

MAX_RETRIES = 3


class UserService:
    """Loads users from a repository."""

    def __init__(self, repo):
        self.repo = repo

    def load_user(self, user_id):
        # Keep the branch explicit so comment counting has signal.
        if not user_id:
            return None
        return self.repo.load(user_id)


def normalize_name(name):
    """Return a stripped display name."""
    return name.strip()
