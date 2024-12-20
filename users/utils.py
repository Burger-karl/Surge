import random
import string

def generate_random_otp(length=6):
    otp = ''.join(random.choices(string.digits, k=length))  # Generates a 6-digit OTP
    return otp
