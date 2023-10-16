import os


def _hash_password(salt, password):
    password = bytearray(salt + password.encode())
    for i in range(len(password)):
        password[i] ^= password[(i + 1) % len(password)]
    for i in range(len(password)):
        temp = password[password[i] ** password[(i + 1) % len(password)] % len(password)]
        password[password[i] ** password[(i + 1) % len(password)] % len(password)] = password[i]
        password[i] = temp
    return password


def encrypt(password, file):
    salt = os.urandom(64)
    password = _hash_password(salt, password)
    password *= int(len(file) / len(password)) + 1
    result = bytearray(file)
    for i in range(len(file)):
        result[i] ^= password[i]
    for i in range(len(file)):
        result[i], result[password[i] ** password[i] % len(result)] = result[password[i] ** password[i] % len(result)], result[i]
    return salt + bytes(result)


def decrypt(password, file):
    salt = file[:64]
    file = file[64:]
    password = _hash_password(salt, password)
    password *= int(len(file) / len(password)) + 1
    result = bytearray(file)
    for i in range(len(file)-1, -1, -1):
        result[i], result[password[i] ** password[i] % len(result)] = result[password[i] ** password[i] % len(result)], result[i]
    for i in range(len(file)):
        result[i] ^= password[i]
    return bytes(result)


if __name__ == '__main__':
    example_password = "Password123"
    print("Password: ", example_password)

    example_data = (b"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc sed diam commodo, efficitur nisi "
                    b"sed, egestas mi. Nam vel consectetur justo. Aliquam sed elit velit. Nullam cursus id orci "
                    b"fringilla laoreet. Aliquam dictum hendrerit libero. Etiam vitae sem at orci consectetur "
                    b"feugiat. Mauris justo massa, lobortis a hendrerit sed, fringilla nec magna. Praesent diam arcu, "
                    b"lacinia id felis non, luctus varius purus. Aliquam erat volutpat. Duis ut enim sed orci "
                    b"placerat vulputate. Curabitur tristique fringilla dui id fermentum. Vestibulum eget consectetur "
                    b"mi, varius viverra purus. Donec at vestibulum leo.")
    print("Data:     ", example_data)

    encrypted = encrypt(example_password, example_data)
    print("Encrypted:", encrypted)

    decrypted = decrypt(example_password, encrypted)
    print("Decrypted:", decrypted)
