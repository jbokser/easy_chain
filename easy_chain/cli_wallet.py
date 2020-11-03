import sys
from os.path import dirname, abspath

bkpath   = sys.path[:]
base_dir = dirname(abspath(__file__))
sys.path.append(dirname(base_dir))

from easy_chain.cli     import yellow, white, red, grey, show_transaction, Response, argument, option
from easy_chain.cli     import command, command_group, tabulate, cli, validate_connected, print_title
from easy_chain.wallet  import BadPassword
from easy_chain.network import wei_to_str, units

sys.path = bkpath



def WalletCLI(group, network, wallet, tokens=[]):

    @command_group(group, 'addr')
    def wallet_addresses():
        """ Referred to addresses """


    if tokens:
        @command_group(group, 'token')
        def wallet_token():
            """ Referred to tokens"""


    @command(wallet_addresses, 'del')
    @argument('address')
    def wallet_del(address):
        """ Delete ADDRESS from the Wallet """

        if address not in wallet:
            raise cli.BadParameter(red('Address not found'))

        del wallet[address]


    @command(wallet_addresses, 'add')
    @argument('private_key')
    @argument('name', nargs=-1)
    @option('-n', '--no-encrypt', 'encrypt', is_flag=True, default=True,
            help='Do not encrypt the private key')
    def wallet_add(private_key, name=None, encrypt=True):
        """ Add an address to the Wallet with its PRIVATE_KEY """
        if name:
            name = ' '.join(list(name))
        else:
            name = None
        try:
            address = wallet.add_priv_key(private_key,
                encrypt = encrypt,
                name    = name)
        except ValueError as e:
            raise cli.BadParameter(red(e))
        print(white('{} has been added.'.format(address)))


    @command(wallet_addresses, 'default')
    @argument('address')
    def wallet_default(address):
        """ Set the default ADDRESS to operate """
        if address not in wallet:
            raise cli.BadParameter(red('Address not found'))
        try:
            wallet.default = address
        except ValueError as e:
            raise cli.BadParameter(red(e))
        print(white('{} has been marked as default.'.format(address)))


    @command(wallet_addresses, 'list')
    def wallet_list():
        """ List of wallet addresses """

        print_title("Addresses")

        if wallet:

            summary = wallet.summary
            summary.sort(key = lambda x:[x['name'] if x['name'] else '',
                                         x['default'],
                                         x['address']])

            for d in summary:
                for k in d.keys():
                    if type(d[k])==bool:
                        d[k] = Response('yes') if d[k] else Response('no')
                address = d['address']
                if d['default']:
                    d['address'] = yellow(address)
                d['balance'] = Response(None)
                if network.is_connected:
                    d['balance'] = white(wei_to_str(network.balance(address)))

            headers = {
                'address': white('Address'),
                'name':    white('Name'),
                'default': white('Default'),
                'encrypt': white('Encrypt'),
                'balance': white('Balance')}

            print(tabulate(summary, headers=headers))

        else:

            print(grey("(none)"))

        print()


    @command(wallet_addresses, 'balance')
    @argument('address')
    @validate_connected(network)
    def wallet_balance(address):
        """ Show the balance off an ADDRESS """

        try:
            address = wallet.Address(address)
        except ValueError as e:
            raise cli.BadParameter(red(e))

        print(white('{} = {}').format(
            address,
            wei_to_str(network.balance(address))))


    @command(group, 'send')
    @argument('to_address')
    @argument('value', type=int)
    @argument('unit', default='wei', type=cli.Choice(units))
    @validate_connected(network)
    def wallet_transfer(to_address, value, unit = 'wei'):
        """
        Transfers VALUE [UNIT] from the default account to TO_ADDRESS

        By default UNIT is wei
        """

        try:
            to_address = wallet.Address(to_address)
        except ValueError as e:
            raise cli.BadParameter(red(e))

        try:
            transaction = network.transfer(
                sign_callback = wallet.sign,
                from_address  = wallet.default,
                to_address    = to_address,
                value         = value,
                unit          = unit)
        except BadPassword:
            raise cli.ClickException(red('Bad private key password'))

        show_transaction(network, transaction)


    if tokens:
        @command(wallet_token, 'send')
        @argument('to_address')
        @argument('value', type=int)
        @argument('token')
        @validate_connected(network)
        def wallet_token_transfer(token, to_address, value):
            """
            Transfers TOKEN VALUE from the default account to TO_ADDRESS
            """

            token = tokens(token)
            if token==None:
                raise cli.BadParameter(red("Token not found."))

            try:
                to_address = wallet.Address(to_address)
            except ValueError as e:
                raise cli.BadParameter(red(e))

            try:
                transaction = token.transfer(
                    sign_callback = wallet.sign,
                    from_address  = wallet.default,
                    to_address    = to_address,
                    value         = value,
                    gas_limit     = 70000)
            except BadPassword:
                raise cli.ClickException(red('Bad private key password'))

            show_transaction(network, transaction)


    if tokens:
        @command(wallet_token, 'balance')
        @argument('address')
        @argument('token')
        @validate_connected(network)
        def wallet_token_balance(address, token):
            """ Show the TOKEN balance off an ADDRESS """

            token = tokens(token)
            if token==None:
                raise cli.BadParameter(red("Token not found."))

            try:
                address = wallet.Address(address)
            except ValueError as e:
                raise cli.BadParameter(red(e))

            print(white('{} = {} {}').format(
                address,
                token.balance(address),
                token.symbol))


    if tokens:
        @command(wallet_token, 'list')
        def wallet_token_list():
            """ List of wallet tokens"""

            print_title("Tokens")

            if tokens:

                summary = [ {'name':        t.name,
                             'symbol':      t.symbol,
                             'address':     t.address,
                             'balance_fnc': t.balance} for t in tokens]

                for d in summary:
                    d['balance'] = Response(None)
                    if network.is_connected and wallet:
                        d['balance'] = white(  d['balance_fnc'](wallet.default)  )
                    del d['balance_fnc']

                headers = {
                    'address': white('Address'),
                    'name':    white('Name'),
                    'symbol':  white('Symbol'),
                    'balance': white('Balance *')}

                print(tabulate(summary, headers=headers))
                print()
                if wallet:
                    print(' * of the default acount {}'.format(wallet.default))
                else:
                    print(' * of the default acount')

            else:

                print(grey("(none)"))

            print()


    if wallet.filename:
        @command(group, 'filename')
        def wallet_filename():
            """ Show wallet config file name """
            print(wallet.filename)



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
