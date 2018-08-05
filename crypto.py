import random
from string import ascii_letters, digits

# ====== Hashing ====== # IN DEVELOPMENT

# ====== Generating ====== # IN DEVELOPMENT

def random_string(length):
    return ''.join(random.choice(ascii_letters + digits) for _ in range(length))