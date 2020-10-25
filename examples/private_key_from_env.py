#!/usr/bin/env python3
import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))

from easy_chain import Wallet

# Non persistent wallet
wallet = Wallet(use_env="PKEY_") 


def main():

    if not 'TEST' in wallet:
        print('')
        print('You must use the environment variable PKEY_TEST')
        print('with the value of a private key.')
        print('')
        print('for example:')
        print('')
        print('PKEY_TEST=0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d ./private_key_from_env.py')
        print('')
        return

    address = wallet['TEST']

    print('')
    print(address)
    print('')



if __name__ == '__main__':
    main()
