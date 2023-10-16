import time
from flask import request
from config import DATABASE_URI, BASE62, ALLOWED_EXTENSIONS  # Import variables from config.py

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_number():
    # Get the IP address and port from the Flask request object
    host, port = request.host.split(':')

    # Remove dots from the IP address
    ip_address = host.replace('.', '')

    # Concatenate the IP address, port, and current Unix timestamp
    unique_number = ip_address + port + str(int(time.time() * 1000))

    # Check if the string is empty after removing '0'
    if not unique_number:
        unique_number = '0'  # If the string is empty, set it to '0'

    return unique_number

def encode(unique_identifier, alphabet):

    unique_number = int(unique_identifier)

    if unique_number == 0:
        return alphabet[0]

    arr = []
    arr_append = arr.append
    _divmod = divmod
    base = len(alphabet)

    while unique_number:
        unique_number, rem = _divmod(unique_number, base)
        arr_append(alphabet[rem])

    arr.reverse()
    return ''.join(arr)