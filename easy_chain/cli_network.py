import sys
from os.path import dirname, abspath

bkpath   = sys.path[:]
base_dir = dirname(abspath(__file__))
sys.path.append(dirname(base_dir))

from easy_chain.cli     import  white, red, grey, Response
from easy_chain.cli     import tabulate, cli, validate_connected
from easy_chain.wallet  import BadPassword
from easy_chain.network import wei_to_str

sys.path = bkpath



def NetworkCLI(group, network, network_conf):


    @group.command(name='gas')
    @validate_connected(network)
    def gas_price():
        """ Show the gas price """
        print(white('gasPrice = {}').format(wei_to_str(network.gas_price)))
        print(white('minimum  = {}').format(wei_to_str(network.minimum_gas_price)))


    @group.command(name='block')
    @validate_connected(network)
    def block_number():
        """ Last block """
        n = network.block_number
        print(white('blockNumber = {}').format(n))
        print(white('timestamp   = {}').format(network.block_timestamp(n)))


    if network_conf.envs:
        @group.command(name='envs')
        def show_envs():
            """ Show environment variables to use """
            print()
            print(tabulate(network_conf.envs.items(),
                headers = ['Environment variable',
                           'Default value']))
            print()


    @group.command(name='default')
    @cli.argument('network', type=cli.Choice(network_conf.network_profiles.keys()))
    def network_default(network):
        """ Set the default NETWORK to operate """

        if network not in network_conf.network_profiles:
            raise cli.BadParameter(red('Network not found'))

        network_conf.selected_profile = network

        print(white('{} has been marked as default.'.format(repr(network))))


    @group.command(name='list')
    def network_list():
        """ List of wallet addresses """
        table = []
        for name, data in network_conf.network_profiles.items():
            row = {}
            row['name'] = name
            row['default'] = Response(name==network_conf.selected_profile)
            for key, value in data.items():
                row[key] = value
            if not 'poa' in row:
                row['poa'] = None
            row['poa'] = Response(row['poa'])
            table.append(row)
            if 'profile' in row:
                del row['profile']
        print()
        headers = {
            'name' :    white('Name'),
            'default':  white('Default'),
            'chain_id': white('Chain ID'),
            'poa':      white('PoA'),
            'uri':      white('URI')}
        print(tabulate(table, headers=headers))
        print()
        print(grey('(config file: {})'.format(network_conf.config_file)))
        print()



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
