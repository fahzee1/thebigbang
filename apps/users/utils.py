import base64
import hashlib, random



def generate_key():
    """
    should only need to use once
    """
    return hashlib.sha224( str(random.getrandbits(256)) ).hexdigest();

def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc))


def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc)
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)

# securly store this somewhere
ENCRYPT_KEY = '0e568a1a226eaa669cb30cd7d37d3e376f45b6ab9de9fe1a600e6e02'

