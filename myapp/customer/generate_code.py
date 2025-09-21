import secrets
import string
from datetime import datetime, timedelta

def generate_verification_code(length=6):
    return ''.join(secrets.choice(string.digits) for _ in range(length))

# Contoh generate kode 6 digit
# kode = generate_verification_code()
# expired_at = datetime.utcnow() + timedelta(minutes=5)  # Berlaku 5 menit