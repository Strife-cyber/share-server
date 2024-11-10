import json
import bcrypt
import hashlib
import os.path

FILE_PATH = os.path.join(os.path.dirname(__file__), "./storage/data.json")  # Corrected file path

def read_json() -> list:
    """
    Reads data from the JSON file storing the user credentials and IDs.
    :return: List containing the JSON data, or an empty list if file not found or empty.
    """
    try:
        with open(FILE_PATH, 'r') as file:
            data = json.load(file)
        print(f"Data successfully read from file.")
        return data
    except FileNotFoundError:
        print("File not found. Creating a new file.")
        return []
    except json.JSONDecodeError as error:
        print(f"Could not decode JSON, returning an empty list. {error}")
        return []

def append_json(new_data: dict) -> None:
    """
    Appends data to the JSON file storing the user credentials and IDs.
    :param new_data: The data to be appended to the JSON file.
    """
    # Read existing data from the file
    data = read_json()

    # Append new data to the list
    if isinstance(data, list):
        data.append(new_data)
    else:
        print("Error: JSON data is not a list. Append operation cancelled.")
        return

    # Write updated data back to the file
    try:
        with open(FILE_PATH, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Data successfully appended to file.")
    except Exception as e:
        print(f"Could not write to {FILE_PATH}: {e}")


def hash_string(data: str) -> str:
    """
    Creates a highly secure hash of the given data using a combination of SHA-256 and bcrypt.
    :param data: The data to be hashed (usually a password or sensitive information).
    :return: The hashed result as a hexadecimal string.
    """
    sha256_hash = hashlib.sha256(data.encode()).hexdigest()

    salt = bcrypt.gensalt()
    bcrypt_hash = bcrypt.hashpw(sha256_hash.encode(), salt)

    return bcrypt_hash.decode()


def verify_hash(data: str, stored_hash: str) -> bool:
    """
    Verifies if the given data matches the stored hash.
    :param data: The data to verify.
    :param stored_hash: The stored hash to compare against.
    :return: True if the data matches the hash, False otherwise.
    """
    # Step 1: SHA-256 hash the input data
    sha256_hash = hashlib.sha256(data.encode()).hexdigest()

    # Step 2: Use bcrypt to check against the stored hash
    return bcrypt.checkpw(sha256_hash.encode(), stored_hash.encode())
