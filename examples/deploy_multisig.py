#!/usr/bin/env python3
import sys, os, json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from easy_chain.cli       import show_transaction, wait_blocks, print_title, print_line, pause, white
from easy_chain.wallet    import Wallet
from easy_chain.network   import Network, wei_to_str
from easy_chain.contracts import MultiSigWallet

network = Network('ganache')

# Non persistent wallet
wallet  = Wallet() 

# Add first deterministic gananche address
wallet.add_priv_key(
    "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d",
    encrypt=False, name='ganache-0')

# Add second deterministic gananche address
wallet.add_priv_key(
    "0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1",
    encrypt=False, name='ganache-1')



def deploy():

    print('Balance of {}: {}'.format(
        '0xd08B...948d',
        white(wei_to_str(network.balance('0xd08B5ac0800267f187AFe2452B7B176E5D98948d')))))

    pause()



    print_title('Deploy Multisig')

    accounts = [wallet.Address('ganache-0'),
                wallet.Address('ganache-1')] 

    required_confirmations = 2

    multisig = MultiSigWallet(network)

    transaction = multisig.deploy(
        wallet.sign,
        wallet.default,
        accounts,
        required_confirmations,
        gas_limit = 3500000)

    response = show_transaction(network, transaction)

    if not response.contract_address:
        print("Can't get the multisig address")
        return

    if not wait_blocks(network):
        print("Can't get the next block")
        return

    multisig.address = response.contract_address

    pause()




    print_title('Transfer 100 ether to the Multisig')

    transaction = network.transfer(
        wallet.sign,
        wallet.default,
        multisig.address,
        value = 100,
        unit = 'ether')

    response = show_transaction(network, transaction)

    if not response:
        return

    if not wait_blocks(network):
        print("Can't get the next block")
        return

    print('Balance of {}: {}'.format(
        multisig.address,
        wei_to_str(network.balance(multisig.address))))

    pause()




    print_title('Submit transfer transaction, 50 ether to 0xd08B...948d')

    transaction = multisig.submit_transaction(
        wallet.sign,
        wallet.default,
        '0xd08B5ac0800267f187AFe2452B7B176E5D98948d',
        value=50,
        unit='ether',
        gas_limit = 3500000)

    response = show_transaction(network, transaction)

    if not response:
        return

    if not wait_blocks(network):
        print("Can't get the next block")
        return

    submit_transaction_id = multisig.get_submit_transaction_id(transaction)

    if submit_transaction_id==None:
        print("Can't get the submit transaction id")
        return

    print('Submit transaction id: {}'.format(submit_transaction_id))

    pause()




    print_title('Confirm transaction')

    wallet.default = wallet.Address('ganache-1')

    transaction = multisig.confirm_transaction(
        wallet.sign,
        wallet.default,
        submit_transaction_id,
        gas_limit = 3500000)

    response = show_transaction(network, transaction)

    if not response:
        return

    if not wait_blocks(network):
        print("Can't get the next block")
        return

    pause()




    print()
    print()
    print('Balance of {}: {}'.format(
        '0xd08B...948d',
        white(wei_to_str(network.balance('0xd08B5ac0800267f187AFe2452B7B176E5D98948d')))))




    print()
    print()
    print_line()
    print()
    print(white(multisig))
    print()
    print(white('Owners:'))
    for owner in multisig.owners:
        print(white('   ' + owner))
    print()
    print(white('Required confirmations = {}'.format(multisig.required)))
    print()



if __name__ == '__main__':
    if network.is_connected:
        deploy()
    else:
        print('For this example you need to have ganache running (in deterministic mode).')
