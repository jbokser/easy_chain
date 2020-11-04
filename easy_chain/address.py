


def Address(addr):

    if addr==None:
        raise ValueError('addr is None')

    if isinstance(addr, int):

        addr = hex(addr)[2:].lower()
        addr = addr[-40:]
        addr = "0" * (40-len(addr)) + addr

    else:

        addr = str(addr).strip().lower()

        if addr.startswith('0x'):
            addr = addr[2:]

        try:
            int(addr, 16)
        except:
            raise ValueError('addr is not hexa')

        if len(addr) != 40:
            raise ValueError('addr has less o more than 40 digits')

    addr = '0x' + addr

    return addr



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))

    for fnc, args, ok_out in [  
            (Address, (1, ),'0x0000000000000000000000000000000000000001'),   
            (Address, (10, ),'0x000000000000000000000000000000000000000a'),   
            (Address, ('d08B5ac0800267f187AFe2452B7B176E5D98948d', ),
            '0xd08b5ac0800267f187afe2452b7b176e5d98948d'),   
            (Address, ('D08B5AC0800267F187AFE2452B7B176E5D98948D', ),
            '0xd08b5ac0800267f187afe2452b7b176e5d98948d'),   
            (Address, ('Bad Addr!', ),ValueError('addr is not hexa')),   
            (Address, ('123456789abc', ),ValueError('addr has less o more than 40 digits')),              
            (Address, (None, ),ValueError('addr is None')),              
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