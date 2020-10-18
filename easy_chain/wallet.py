from click                import prompt
from os.path              import dirname, abspath, expanduser
from sys                  import path, argv
from web3                 import Web3
from web3.exceptions      import InvalidAddress
from eth_account          import Account
from tabulate             import tabulate
from web3.auto            import w3
from eth_account.messages import encode_defunct
from os                   import environ


path.append(dirname(__file__))

from simple_decoder import encode, decode
from dict_tools     import PersistentDict, reverse_dcit



if __name__ == '__main__':
    work_dir = dirname(dirname(abspath(__file__)))
else:
    work_dir = dirname(abspath(argv[0]))
home_dir = expanduser("~")



def prompt_private_key_pass(key, confirmation=False):
    return prompt(
        'Enter private key password for {}'.format(key),
        type = str,
        hide_input = True,
        confirmation_prompt = confirmation)



Address = lambda value: str(Web3.toChecksumAddress(str(value)))



AddressFromPrivateKey = lambda value: str(Account.privateKeyToAccount(value).address)



class BadPassword(Exception):
    pass



class WalletBase(dict):


    def __init__(self, storage):

        self.password = None
        self.encrypt  = True
        self._names    = {}

        self._storage  = storage

        if not 'wallet' in storage:
            storage['wallet'] = {'default':    None,
                                 'addresses': {},
                                 'names':     {}}

        self._default = storage['wallet']['default']

        for key, value in dict(storage['wallet']['addresses']).items():
            dict.__setitem__(self, key, value)
        for key, value in dict(storage['wallet']['names']).items():
            self._names[key] = value


    def clean_up(self):
        for key in list(self.keys()):
            del self[key]


    def _dump(self):
        self._storage['wallet'] = {'default':   self._default,
                                   'addresses': dict(self),
                                   'names':     self._names}


    def _get_password(self, key, confirmation=False):
        if self.password:
            pwd = self.password
            self.password = None
        else:
            pwd = prompt_private_key_pass(key, confirmation)
        return pwd


    def Address(self, address):
        address = self.get_by_name(address, address)
        address = Address(address)
        return address


    def __contains__(self, key):
        try:
            return dict.__contains__(self, self.Address(key))
        except ValueError:
            return False


    def __getitem__(self, key):

        key = self.Address(key)

        value = dict.__getitem__(self, key)

        try:
            valid_key = AddressFromPrivateKey(value)
        except:
            valid_key = None

        if valid_key and valid_key == key:
            return value

        try:
            value = decode(self._get_password(key), value)
        except ValueError:
            raise BadPassword

        return value


    def __setitem__(self, key, value):

        key = self.Address(key)

        value     = str(value)
        key       = Address(key)
        valid_key = AddressFromPrivateKey(value)

        if valid_key != key:
            raise ValueError

        if self.encrypt:
            value = encode(self._get_password(key, confirmation=True), value)

        dict.__setitem__(self, key, value)

        if len(self)==1:
            self._default = key

        self._dump()


    def __delitem__(self, key):

        key = self.Address(key)

        dict.__delitem__(self, key)

        if key in self._names:
            del self._names[key]

        if key == self._default:
            self._default = None

        if len(self)==1:
            self._default = self.addresses[0]

        self._dump()


    def __repr__(self):
        return object.__repr__(self)

    @property
    def summary(self):
        out = []
        for address in self.addresses:
            out.append({'address': address,
                        'name': self.get_name(address),
                        'default': self.get_is_default(address),
                        'encrypt': self.get_is_encrypt(address)})
        return out


    def __str__(self):

        summary = self.summary

        for d in summary:
            for k in d.keys():
                if type(d[k])==bool:
                    d[k] = 'yes' if d[k] else 'no'

        headers = {
            'address': 'Address',
            'name':    'Name',
            'default': 'Default',
            'encrypt': 'Encrypt'}

        return str(tabulate(summary, headers=headers))


    @property
    def addresses(self):
        return list(dict.keys(self))


    @property
    def default(self):
        return self._default


    @default.setter
    def default(self, value):
        value = self.Address(value)
        if value in self:
            self._default = value
            self._dump()
        else:
            raise ValueError('Address not in wallet')


    @property
    def default_private_key(self):
        if not self.default:
            return None
        return self[self.default]


    def set_name(self, address, name):
        address = self.Address(address)
        if address not in self:
            raise ValueError('Address not in wallet')
        if address in self._names and not name:
            del self._names[address]
            self._dump()
            return
        if name:
            self._names[address] = str(name)
            self._dump()


    def del_name(self, address):
        self.set_name(address, None)


    def get_name(self, address):
        address = self.Address(address)
        if address not in self:
            raise ValueError('Address not in wallet')
        if address not in self._names:
            return None
        out = self._names[address]
        if out:
            return str(out)
        return None


    def get_by_name(self, name, default=None):
        return reverse_dcit(self._names).get(name, default)


    def get_is_encrypt(self, address):
        address = self.Address(address)
        if address not in self:
            raise ValueError('Address not in wallet')
        value = dict.__getitem__(self, address)
        try:
            out = AddressFromPrivateKey(value)!=address
        except:
            out = True
        return out


    def sign(self, data, address = None):
        if not address:
            address = self.default
        if not address:
            raise ValueError('Address not in wallet')
        address = self.Address(address)
        if address not in self:
            raise ValueError('Address not in wallet')

        if type(data) in [dict]:
            signed = w3.eth.account.sign_transaction(data, self[address])
            return signed.rawTransaction.hex()

        message        = encode_defunct(text=str(data))
        signed_message = w3.eth.account.sign_message(message, private_key=self[address])
        signature      = signed_message.signature.hex()

        return signature


    def verify(self, sign, data = None, address = None):
        if not address:
            address = self.default
        if not address:
            raise ValueError('Address not in wallet')
        address = self.Address(address)
        if address not in self:
            raise ValueError('Address not in wallet')

        if type(data) in [dict]:
            try:
                valid_address = w3.eth.account.recover_transaction(sign)
                return valid_address == address
            except:
                return False

        if not data:
            return False

        message        = encode_defunct(text=str(data))
        valid_address = w3.eth.account.recover_message(message, signature=sign)

        try:
            return valid_address == address
        except:
            return False


    def get_is_default(self, address):
        address = self.Address(address)
        if address not in self:
            raise ValueError('Address not in wallet')
        return address==self.default


    def add_priv_key(self, value, encrypt = True, name = None):

        value   = str(value)
        address = AddressFromPrivateKey(value)

        pre_encrypt   = self.encrypt
        self.encrypt  = encrypt
        self[address] = value
        self.encrypt  = pre_encrypt

        if name:
            self.set_name(address, name)

        return address


class Wallet(WalletBase):

    def __init__(self,
                 profile   = None,
                 storage   = None,
                 json_file = '{home_dir}/.easy_chain/wallets/{profile}.json',
                 use_env   = False):

        if not profile and '{profile}' in json_file:
            json_file = None

        if json_file:
            json_file = json_file.format(work_dir = work_dir,
                                         home_dir = home_dir,
                                         profile  = profile)
            storage = PersistentDict(json_file) # persistent wallet

        if not storage:
            if not isinstance(storage, dict):
                storage = {} # non persistent wallet

        WalletBase.__init__(self, storage)

        if use_env:
            for key, value in environ.items():
                if key.startswith(use_env):
                    name = key[len(use_env):]
                    try:
                        self.add_priv_key(value, encrypt=False, name = name)
                    except:
                        pass



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))

    wallet = Wallet() # non persistent wallet

    # Some test data
    password = '12345'
    wallet.add_priv_key(
        "4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d",
        encrypt = False, name = "ganache_1")
    wallet.password = password
    wallet.add_priv_key(
        "4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1a",
        encrypt = True, name = "test_a")
    wallet.password = password
    wallet.add_priv_key(
        "4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1c",
        encrypt = True, name = "test_b")
    wallet.add_priv_key(
        "4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b10",
        encrypt = False)
    print()
    print('Some test data')
    print('==== ==== ====')
    print()
    print('Password: {}'.format(password))
    print()
    print(wallet)
    print()

    for data, signed in [
            ("Hello world!", "0x41229c026586cfb2125f6cf1272a4e240ebb9ce3c3e8a50dfdcaaf5d57b5ca4565a751fc825ad6505a71d513e0c48ee1e8500e4fe192b2394936853fd25549861b"),
            ({'to':       '0xF0109fC8DF283027b6285cc889F5aA624EaC1F55',
              'value':    1000000000,
              'gas':      2000000,
              'gasPrice': 234567897654321,
              'nonce':    0,
              'chainId':  1},
             "0xf86a8086d55698372431831e848094f0109fc8df283027b6285cc889f5aa624eac1f55843b9aca008026a0e7c96c14f9adc4d42b18767f25b2f204fcd1ac467d593475630f07fcc0be9739a07dc995ebe234899b140ca870f81d0a1af2d883381c38adc2ee2780dfa32334c1")
        ]:

        for fnc, args, ok_out in [
                (wallet.sign, (data, ),  signed),
                (wallet.verify, (signed, data), True)
            ]:

            out = fnc(*args)

            if out == ok_out:
                eval_ = 'Ok!'
            else:
                eval_ = 'Return: {}, Error!'.format(out)

            message = 'Test: wallet.{}({}), Expect: {}, {}'
            message = message.format(
                fnc.__name__,
                ', '.join([ repr(x) for x in list(args)]),
                repr(ok_out),
                eval_)

            print(message)