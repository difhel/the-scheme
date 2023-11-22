import binascii

def crc32(data: str) -> str:
    return hex(binascii.crc32(data.encode()) % (1 << 32))[2:]

print(crc32("bot id: int, bot: Bot = ChatMember"))