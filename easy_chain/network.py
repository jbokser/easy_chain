import json, datetime
from web3            import Web3, HTTPProvider
from web3.exceptions import InvalidAddress, ValidationError, BadFunctionCallOutput, TransactionNotFound
from web3.middleware import geth_poa_middleware
from sys             import path
from os.path         import dirname

path.append(dirname(__file__))

from conf           import get as config
from simple_decoder import hash_


def config_call_back_first(options):
    return {
        'network_profile': options['selected_profile']
    }

def config_call_back_second(options):
    profiles = options['profiles']
    opt      = profiles[network_profile]
    return {
        'network_conf':     opt,
        'network_profiles': profiles
    }

for call_back in [config_call_back_first,
                  config_call_back_second]:
    config(locals(),
           call_back,
           ['network.json', 'network_default.json'],
           'network',
           env_pre = 'wallet')



units = ['wei', 'kwei', 'mwei', 'gwei', 'nanoether', 'microether',
         'milliether', 'ether']



def wei_to_tuple(value):
    """ wei --> (value, str_unit) """
    value    = int(value)
    str_unit = 'wei'
    if value > 1000:
        for str_unit in ['Kwei', 'Mwei', 'Gwei', 'Microether', 'Milliether',
                         'Ether', 'Kether', 'Mether', 'Gether', 'Tether']:
            value = value/1000
            if value<1000:
                break
    return (value, str_unit)



def wei_to_str(value):
    """ wei --> str """
    return '{0:.2f} {1}'.format(*wei_to_tuple(value))



class NetworkBase():


    def __init__(self, uri, chain_id, profile, poa=False):
        self.profile = profile
        self._uri = uri
        self._cahin_id = chain_id
        self.web3 = Web3(HTTPProvider(uri))
        if poa:
            self.web3.middleware_onion.inject(
                geth_poa_middleware, layer=0)


    @property
    def uri(self):
        """ Returns where it connects """
        return self._uri


    @property
    def chain_id(self):
        """ Returns then chain ID """
        return self._cahin_id


    def dict_constructor(self, properties=[]):
        out = {}
        for attr_name in dir(self):
            if attr_name[0]!='_' and attr_name not in ['as_dict', 'json']:
                attr = getattr(self, attr_name)
                if not '__call__' in dir(attr):
                    if not(properties) or (attr_name in properties):
                        out[attr_name] = attr


    @property
    def as_dict(self):
        return {'profile':  self.profile,
                'uri':      self.uri,
                'chain_id': self.chain_id}


    @property
    def json(self):
        return json.dumps(self.as_dict, indent=4, sort_keys=True)


    @property
    def uuid(self):
        return hash_(self.json)


    @property
    def is_connected(self):
        """ Returns if connected """
        return self.web3.isConnected()


    def __bool__(self):
        return self.is_connected


    @property
    def gas_price(self):
        """ Gas price """
        return self.web3.eth.gasPrice


    @property
    def minimum_gas_price(self):
        """ Gas Price """
        try:
            return Web3.toInt(hexstr=self.web3.eth.getBlock('latest').minimumGasPrice)
        except AttributeError:
            return self.web3.eth.gasPrice


    @property
    def block_number(self):
        """ Block number """
        return self.web3.eth.blockNumber


    def balance(self, address):
        """ Get the balance of an address """
        return self.web3.eth.getBalance(address)


    def transaction_count(self, address, nonce_method = "pending"):
        """ Get the transaction count of an address """
        return self.web3.eth.getTransactionCount(address, nonce_method)


    def send_transaction(self, transaction):
        """ Send raw transaction """
        return self.web3.eth.sendRawTransaction(transaction).hex()


    def get_block(self, *args, **kargs):
        """ Get a block """
        return self.web3.eth.getBlock(*args, **kargs)


    def block_timestamp(self, block):
        """ Block timestamp """
        block_timestamp = self.web3.eth.getBlock(block).timestamp
        return datetime.datetime.fromtimestamp(block_timestamp)
        
        
    @staticmethod
    def Address(value):
        return str(Web3.toChecksumAddress(str(value)))


    def balance_block_number(self, address, block_number=0):
        """ Balance of the address """
        return self.web3.eth.getBalance(self.Address(address), block_number)
        

    def get_transaction_by_hash(self, transaction_hash):
        """ Transaction by hash """
        return self.web3.eth.getTransaction(transaction_hash)


    def get_transaction_receipt(self, transaction_hash):
        """ Get transaction receipt """

        def normalize(value):
            if 'items' in dir(value):
                value = dict(value.items())
                for key in list(value.keys()):
                    value[key] = normalize(value[key])
            if 'hex' in dir(value):
                value = value.hex()
            if isinstance(value, list):
                value = [normalize(x) for x in value]
            return value

        try:
            return normalize(self.web3.eth.getTransactionReceipt(transaction_hash))
        except TransactionNotFound:
            return None


    def transfer(self,
                 sign_callback,
                 from_address,
                 to_address,
                 value,
                 unit='wei',
                 gas_limit = 100000):
        """ Transfer """

        from_address = self.Address(from_address)
        to_address   = self.Address(to_address)

        value = self.web3.toWei(value, unit)

        nonce = self.transaction_count(from_address)

        transaction = dict(chainId  = self.chain_id,
                           nonce    = nonce,
                           gasPrice = self.gas_price,
                           gas      = gas_limit,
                           to       = to_address,
                           value    = value)

        signed_transaction = sign_callback(transaction)

        return self.send_transaction(signed_transaction)


    def transaction(self,
                    sign_callback,
                    contract_function,
                    from_address,
                    value        = 0,
                    unit         = 'wei',
                    gas_limit    = 0,
                    gas_price    = 0,
                    nonce_method = "pending"):

        value = self.web3.toWei(value, unit)

        gas_estimate = contract_function.estimateGas()

        if not gas_limit:
            gas_limit = gas_estimate

        if gas_estimate > gas_limit:
            raise Exception("Gas estimated is bigger than gas limit")

        if not gas_price:
            gas_price = self.minimum_gas_price

        from_address = self.Address(from_address)

        nonce = self.transaction_count(from_address, nonce_method = nonce_method)

        transaction_dict = dict(chainId = self.chain_id,
                                nonce    = nonce,
                                gasPrice = gas_price,
                                gas      = gas_limit,
                                value    = value)

        transaction = contract_function.buildTransaction(transaction_dict)

        signed_transaction = sign_callback(transaction)

        return self.send_transaction(signed_transaction)



class Network(NetworkBase):

    def __init__(self, profile=None, uri=None, chain_id=None, poa=False):

        if not profile:
            profile = network_profile
        
        if profile in network_profiles:
            kargs = network_profiles[profile]
        else:
            kargs = {}

        if uri:
            kargs['uri'] = uri

        if chain_id:
            kargs['chain_id'] = chain_id

        if poa:
            kargs['poa'] = poa

        kargs['profile'] = profile       
        NetworkBase.__init__(self, **kargs)



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    print()
    network = Network()
    properties = ['profile', 'uri', 'chain_id', 'uuid', 'is_connected']
    if network:
        properties += [ 'block_number', 'gas_price']
    for p in properties:
        value = getattr(network, p)
        print("network.{} = {}".format(p, repr(value)))
