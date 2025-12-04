import random

from rsa_core import (
    GenerateKeyPair, 
    Encrypt, 
    Decrypt, 
    Sign, 
    Verify, 
    SendKey, 
    ReceiveKey
)

n_A = 8372190852798214821623431570334256074524018441668275433195376990410146326320024625669342500601693631965816215753716795733874186331644146850006264893123787
e_A = 5260489977338744596016032448517040574147790554545505304921812313905437394271557704959311054120439340370996736264115824758238217557139290807927827721489625
d_A = 5610398905024919020128749168656444673136228187176100597783286353700434893096092431947792948178033269305282325619101874304221580447724826423385550293553185
p_A = 91439515837855219274923357742254755691904705087646001447278390085368451083863
q_A = 91559877325293050039197386182834311722525180486820365414104157091682691941549

n_B, e_B = 0x8CDA1BDABD69CABCC0087C2F6EFF4438B3EBA93AF56733783232D22123666867, 0x10001

print("Параметри скрипта")

print(f"n = {hex(n_A)}")
print(f"e = {hex(e_A)}")
print(f"d = {hex(d_A)}")
print(f"p = {hex(p_A)}")
print(f"q = {hex(q_A)}")

print("Відомі параметри сервера")

print(f"n = {hex(n_B)}")
print(f"e = {hex(e_B)}")

print("--- Зашифрування повідомлення для сервера --- ")
M = "aboba"
print(f"M = {M}")
Mbytes = 0x61626F6261
print(f"Mbytes = {Mbytes}")
C = Encrypt(Mbytes, (n_B, e_B))
Cbytes = hex(C)[2:].upper()
print(f"C = {C}")
print(f"Cbytes = {Cbytes}")

print("--- Розшифрування повідомлення від сервера --- ")
BIT_LENGTH = 256 

C = 0x8706A9CA09A94917B6D2EF7B52077D3C8D29182EA90753B576A09697ED7E304D1C798BD61ECDBD49C699C1FE6641C109306EDC5D4DC87DEDA774ECB8F6D28B74
M = Decrypt(C, (d_A, p_A, q_A))
hex_string = hex(M)[2:] 
if len(hex_string) % 2 != 0:
    hex_string = "0" + hex_string
M_bytes = bytes.fromhex(hex_string)
Mtext = M_bytes.decode("ascii") 

print(f"M = {M}")
print(f"Mtext: {Mtext}")

print("--- Верифікація цифрового підпису ---")
signature = 0x6CA8E6235403F3983E4681DF5A6AABA1598BE061D8E41034F934ED9A8DE3A4AB
print(f"signature: {signature}")
is_valid = Verify("aboba", signature, (n_B, e_B))
print(f"Valid: {is_valid}")

print("--- Підписування ---")
signature = Sign("aboba", (d_A, p_A, q_A))
print("message = aboba")
print(f"signature = {hex(signature)}")

print("--- Надсилання ключа ---")
k_secret = 432462
print(f"k_secret = {hex(k_secret)}") 
k1_S1_pair = SendKey(k_secret, (d_A, p_A, q_A), (n_B, e_B))
print(f"k1 = {hex(k1_S1_pair[0])}\nS1 = {hex(k1_S1_pair[1])}")


print("--- Отримання ключа ---")
k = 0x1A217A389CBA49FE2A96C40A5F5392EC8D13DDBB521FC3114DC687071C5BD36854A3A59C8AE6FCF7DE4904C3217FF4F0C6384419E02E13222BB37B18A611D689
s = 0x6C042351B5B039304CCE36C4C5FC75E8F9452B3EC07FFC842F8F017DA5191F5BE59D83F9DB1A5A2547A7946C68CE35B28EC818058D4AA194F72F30547C8BE5B9
print(f"k = {hex(k)}")
print(f"s = {hex(s)}")
k_received, auth_status = ReceiveKey((k, s), (d_A, p_A, q_A), (n_B, e_B))

print(f"Абонент B отримав значення k' = {k_received}")
print(f"Статус автентифікації: {auth_status}")