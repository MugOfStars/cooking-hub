"""Print the Argon2 hash of a password, for the AUTH_PASSWORD_HASH setting.

    uv run python -m app.hash_password

Kept apart from app.auth so it runs without any settings configured.
"""

from getpass import getpass

from argon2 import PasswordHasher


def main() -> None:
    password = getpass("Password: ")
    if password != getpass("Repeat: "):
        raise SystemExit("Passwords don't match.")
    print(PasswordHasher().hash(password))


if __name__ == "__main__":
    main()
