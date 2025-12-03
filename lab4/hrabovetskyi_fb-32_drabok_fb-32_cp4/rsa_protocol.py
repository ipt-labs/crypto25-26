from rsa_core import Encrypt, Decrypt, Sign, Verify


def SendKey(k, sender_private, sender_public, receiver_public):
    """
    Абонент А формує повідомлення (k1, S1)
    """
    n, e = sender_public
    n1, e1 = receiver_public

    if n1 < n:
        raise ValueError("Error: Receiver's modulus n1 must be >= Sender's modulus n")

    S = Sign(k, sender_private)

    k1 = Encrypt(k, receiver_public)

    S1 = Encrypt(S, receiver_public)

    return k1, S1


def ReceiveKey(package, receiver_private, sender_public):
    """
    Абонент В отримує k та перевіряє підпис
    """
    k1, S1 = package

    k = Decrypt(k1, receiver_private)

    S = Decrypt(S1, receiver_private)

    is_valid = Verify(k, S, sender_public)

    return k, is_valid