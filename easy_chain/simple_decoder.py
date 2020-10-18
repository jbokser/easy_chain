import base64, hashlib



def raw_encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()



def raw_decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)



def hash_(value):
    return hashlib.sha256(str(value).encode('utf-8')).hexdigest()



def encode(key, clear):
    raw = '{}{}'.format(hash_(clear), str(clear))
    return raw_encode(hash_(key), raw)



def decode(key, enc):
    try:
        raw = raw_decode(hash_(key), enc)
        value, test_hash = raw[64:], raw[:64]
    except:
        raise ValueError
    if hash_(value) != test_hash:
        raise ValueError
    return value



if __name__ == '__main__':

    print("File: {}, Ok!".format(repr(__file__)))

    key     = "Some key!"
    base    = "Hello world!"
    encoded = "w4diwppkbMKWZMKTwpZkw4jCnW_CnMKYwp1vwpViwpplamDCmmZkasOFw4dxbcKeZWZrwplkw4VrwpzDhMKawpNnasOGw4jDh8OJwpnClsKSbMKXw4xlwpLDhMKUwpvDi21kwpjCrMKXw5HCncKmUcKnwqDCo8Kew4rChw=="

    for fnc, args, ok_out in [  
            (encode, (key, base),   encoded),
            (decode, (key,encoded), base)      
        ]:

        out = fnc(*args)

        if out == ok_out:
            eval_ = 'Ok!'
        else:
            eval_ = 'Return: {}, Error!'.format(out)

        message = 'Test: {}({}), Expect: {}, {}'
        message = message.format(
            fnc.__name__,
            ', '.join([ repr(x) for x in list(args)]),
            repr(ok_out),
            eval_)

        print(message)
