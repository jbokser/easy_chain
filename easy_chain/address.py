from eth_account import Account
from web3        import Web3



keccak = Web3.keccak



def Address(addr: str or int) -> str:
    """ Address validator """

    if addr==None:
        raise ValueError('addr is None')

    if isinstance(addr, int):

        addr = hex(addr)[2:]
        addr = addr[-40:]
        addr = "0" * (40-len(addr)) + addr

    else:

        addr = str(addr).strip()

        if addr.startswith('0x'):
            addr = addr[2:]

        try:
            int(addr, 16)
        except:
            raise ValueError('addr is not hexa')

        if len(addr) != 40:
            raise ValueError('addr has less o more than 40 digits')

    addr = '0x' + addr.lower()

    return addr



def AddressFromPrivateKey(private_key: str)-> str:
    """ Get the Addres from Private Key """

    if private_key==None:
        raise ValueError('private_key is None')

    return Address(str(Account.from_key(private_key).address))



def AddressWithChecksum(addr, chain_id=1, adopted_eip1191=[30, 31]):
    """ Get an Address with the chacksum encode """

    addr     = Address(addr)
    chain_id = int(chain_id)

    if chain_id in adopted_eip1191:
        hash_input = str(chain_id) + addr
    else:
        hash_input = addr[2:]

    addr = addr[2:]

    hash_output = keccak(hash_input.encode('utf8')).hex()[2:]
    aggregate   = zip(addr, hash_output)

    out = [ c.upper() if int(a, 16) >= 8 else c for c, a in aggregate ]
    out = '0x' + ''.join(out)

    return out



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))

    for fnc, args, ok_out in [

            (Address, (1, ),'0x0000000000000000000000000000000000000001'),

            (Address, (10, ),'0x000000000000000000000000000000000000000a'),

            (Address, ('d08B5ac0800267f187AFe2452B7B176E5D98948d', ),
            '0xd08b5ac0800267f187afe2452b7b176e5d98948d'),   
            
            (Address, ('D08B5AC0800267F187AFE2452B7B176E5D98948D', ),
            '0xd08b5ac0800267f187afe2452b7b176e5d98948d'),   
            
            (Address, ('Bad Addr!', ), ValueError('addr is not hexa')),   
            
            (Address, ('123456789abc', ), ValueError('addr has less o more than 40 digits')),              
            
            (Address, (None, ), ValueError('addr is None')),

            (AddressFromPrivateKey, (None, ), ValueError('private_key is None')),
            
            (AddressFromPrivateKey, ('4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d', ),
                '0x90f8bf6a479f320ead074411a4b0e7944ea8c9c1'),

            (AddressWithChecksum, ('0xd08b5ac0800267f187afe2452b7b176e5d98948d', 1),
                '0xd08B5ac0800267f187AFe2452B7B176E5D98948d'),
            
            (AddressWithChecksum, ('0xd08b5ac0800267f187afe2452b7b176e5d98948d', 30),
                '0xD08b5Ac0800267f187Afe2452B7B176E5d98948D'),
            
            (AddressWithChecksum, ('0xd08b5ac0800267f187afe2452b7b176e5d98948d', 31),
                '0xD08B5AC0800267f187AfE2452B7B176E5D98948D')
            
        ]:

        try:
            out = fnc(*args)
        except Exception as e:
            out = e

        if (isinstance(ok_out, Exception) and isinstance(out, Exception)
                and out.args==ok_out.args):
            eval_ = 'Ok!'
        elif out == ok_out:
            eval_ = 'Ok!'
        else:
            eval_ = 'Return: {}, Error!'.format(repr(out))

        if isinstance(ok_out, Exception): 
            message = 'Test: {}({}), Expect error: {}, {}'
        else:
            message = 'Test: {}({}), Expect: {}, {}'

        message = message.format(
            fnc.__name__,
            ', '.join([ repr(x) for x in list(args)]),
            repr(ok_out),
            eval_)

        print(message)