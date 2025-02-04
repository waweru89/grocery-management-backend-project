import os
import binascii

# Generate a random 24-byte secret key
secret_key = binascii.hexlify(os.urandom(24)).decode()

# Print or save the key to your .env file
print(f"Generated Secret Key: {secret_key}")
