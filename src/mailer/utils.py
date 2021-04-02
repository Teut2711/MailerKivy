
from cryptography.fernet import Fernet
import json
import binascii

def decode_data(encrypted_data):
    try:
        key = encrypted_data["license_key"].encode("utf-8")
        f = Fernet(key)
        decrypted_data = json.loads(f.decrypt(encrypted_data["token"].encode("utf-8")).decode("utf-8"))
    except binascii.Error:
        return False
    else:
        return decrypted_data
