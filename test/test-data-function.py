from client.data_function import append_json, read_json, hash_string, verify_hash

new_entry = {"email": "royce.dupont@example.com", "password": "2500*dark", "id": "acvbf89"}
append_json(new_entry)

upload_data = read_json()
print("Upload data:", upload_data)

data = "SuperSecretPassword123!"
hashed_result = hash_string(data)
print("Stored Hash:", hashed_result)

# Verify the password later
is_match = verify_hash(data, hashed_result)
print("Does the input match the stored hash?", is_match)