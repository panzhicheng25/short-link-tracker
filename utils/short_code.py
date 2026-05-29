CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(CHARS)

def encode(num):
    if num == 0:
        return CHARS[0]
    result = []
    while num > 0:
        result.append(CHARS[num % BASE])
        num //= BASE
    return ''.join(reversed(result))

def decode(short_code):
    num = 0
    for c in short_code:
        num = num * BASE + CHARS.index(c)
    return num
