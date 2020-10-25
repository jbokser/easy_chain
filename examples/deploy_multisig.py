#!/usr/bin/env python3
import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))

from easy_chain.cli       import show_transaction, wait_blocks, print_title, print_line, pause, white
from easy_chain.wallet    import WalletGanache
from easy_chain.network   import Network, wei_to_str
from easy_chain.contracts import MultiSigWallet

network = Network('ganache')

# Non persistent wallet with the deterministic Gananche address
wallet = WalletGanache() 
wallet.default = wallet.Address(1)



def deploy():

    print('Balance of {}: {}'.format(
        '0xd08B...948d',
        white(wei_to_str(network.balance('0xd08B5ac0800267f187AFe2452B7B176E5D98948d')))))

    pause()



    print_title('Deploy Multisig')

    accounts = [wallet.Address(1),
                wallet.Address(2)] 

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

    wallet.default = wallet.Address(2)

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
