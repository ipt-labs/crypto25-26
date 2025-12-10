from rsa_system import Encrypt

server_n_hex = "9FA9DCC0063E4697478D96F7CFE39EF0A4182D8C641EC2BC6E4CC8934572EBE42164D75B12660DEDAA4F793E153319E3BF273516E3D5EEDFBDA7B2CA4F428E65"
server_e_hex = "10001"

server_n = int(server_n_hex, 16)
server_e = int(server_e_hex, 16)

print(f"Server N (int): {server_n}")
print(f"Server E (int): {server_e}")

message = 0x3039 # 12345
print(f"\nНаше повідомлення: {message}")

ciphertext = Encrypt(message, server_e, server_n)

ciphertext_hex = hex(ciphertext)[2:].upper()

print(f"\nЗашифроване повідомлення (HEX):")
print(ciphertext_hex)
print("-" * 60)