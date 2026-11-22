import os

from argon2 import PasswordHasher

TEST_PASSWORD = "correct-horse-test-only"

# Set before the app is imported, so settings load with known auth values. Real
# environment variables take precedence over the developer's .env file.
os.environ["AUTH_ENABLED"] = "true"
os.environ["AUTH_PASSWORD_HASH"] = PasswordHasher().hash(TEST_PASSWORD)
os.environ["SESSION_SECRET"] = "test-session-secret-not-used-anywhere-real"
os.environ["COOKIE_SECURE"] = "true"
