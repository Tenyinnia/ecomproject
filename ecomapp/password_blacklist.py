COMMON_PASSWORDS = [
    "password", "123456", "qwerty", "password123", "admin", "welcome", "letmein", "monkey"
]

def is_common_password(password):
    return password.lower() in COMMON_PASSWORDS
