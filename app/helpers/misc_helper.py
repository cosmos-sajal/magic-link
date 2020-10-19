import random

def get_random_string(length=10):
    """
    Generates a random string of fixed length
    """

    string = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

    return ''.join(random.choice(string) for i in range(length))
