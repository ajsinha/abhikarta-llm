import hashlib


def hash_password_md5(password):
    """
    Hashes a password using the MD5 algorithm.
    """
    # Convert the string password to bytes
    password_bytes = password.encode('utf-8')

    # Create the MD5 hash object
    m = hashlib.md5()

    # Update the hash object with the password bytes
    m.update(password_bytes)

    # Get the hexadecimal representation of the hash
    return m.hexdigest()


def verify_password_md5(password_attempt, stored_hash):
    """
    Verifies a password attempt against a previously stored MD5 hash.
    """
    # Hash the new password attempt
    new_hash = hash_password_md5(password_attempt)

    # Compare the new hash with the stored hash
    return new_hash == stored_hash


# --- Usage Example ---

# 1. Hashing the Password (What you would store in the database)
user_password = "admin123"
stored_password_hash = hash_password_md5(user_password)

print(f"Original Password: {user_password}")
print(f"Stored MD5 Hash:   {stored_password_hash}")

# 2. Verification (When the user tries to log in)
print("-" * 30)

# Successful verification
login_attempt_correct = "admin123"
is_verified_correct = verify_password_md5(login_attempt_correct, stored_password_hash)

print(f"Attempt 1 (Correct): '{login_attempt_correct}' -> Verified: {is_verified_correct}")

# Failed verification
login_attempt_incorrect = "WrongPassword"
is_verified_incorrect = verify_password_md5(login_attempt_incorrect, stored_password_hash)

print(f"Attempt 2 (Incorrect): '{login_attempt_incorrect}' -> Verified: {is_verified_incorrect}")