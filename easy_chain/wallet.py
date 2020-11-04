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

bkpath   = path[:]
base_dir = dirname(abspath(__file__))
path.append(dirname(base_dir))

from easy_chain.simple_decoder import encode, decode
from easy_chain.dict_tools     import PersistentDict, reverse_dcit
from easy_chain.address        import AddressWithChecksum as Address
from easy_chain.address        import AddressWithChecksumFromPrivateKey as AddressFromPrivateKey

path = bkpath



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

        if storage['wallet']['default']: 
            self._default = Address(storage['wallet']['default'])
        else:
            self._default = None

        for key, value in dict(storage['wallet']['addresses']).items():
            try:
                key = Address(key)
            except:
                key = None
            if key:
                dict.__setitem__(self, key, value)

        for key, value in dict(storage['wallet']['names']).items():
            try:
                key = Address(key)
            except:
                key = None
            if key:
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
        address = str(address)
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
    def filename(self):
        try:
            return self._storage.filename
        except:
            return None


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
                valid_address = Address(w3.eth.account.recover_transaction(sign))
                return valid_address == address
            except:
                return False

        if not data:
            return False

        message       = encode_defunct(text=str(data))
        valid_address = Address(w3.eth.account.recover_message(message, signature=sign))

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
                 use_env   = False,
                 **kargs):

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

        for key, value in kargs.items():
            self.add_priv_key(value, encrypt=False, name=key)



class WalletGanache(Wallet):

    def __init__(self):
        Wallet.__init__(self, **{
            '0':  '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d',
            '1':  '0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1',
            '2':  '0x6370fd033278c143179d81c5526140625662b8daa446c22ee2d73db3707e620c',
            '3':  '0x646f1ce2fdad0e6deeeb5c7e8e5543bdde65e86029e2fd9fc169899c440a7913',
            '4':  '0xadd53f9a7e588d003326d1cbf9e4a43c061aadd9bc938c843a79e7b4fd2ad743',
            '5':  '0x395df67f0c2d2d9fe1ad08d1bc8b6627011959b79c53d7dd6a3536a33ab8a4fd',
            '6':  '0xe485d098507f54e7733a205420dfddbe58db035fa577fc294ebd14db90767a52',
            '7':  '0xa453611d9419d0e56f499079478fd72c37b251a94bfde4d19872c44cf65386e3',
            '8':  '0x829e924fdf021ba3dbbc4225edfece9aca04b929d6e75613329ca6f1d31c0bb4',
            '9':  '0xb0057716d5917badaf911b193b12b910811c1497b5bada8d7711f758981c3773',
            '10': '0x77c5495fbb039eed474fc940f29955ed0531693cc9212911efd35dff0373153f',
            '11': '0xd99b5b29e6da2528bf458b26237a6cf8655a3e3276c1cdc0de1f98cefee81c01',
            '12': '0x9b9c613a36396172eab2d34d72331c8ca83a358781883a535d2941f66db07b24',
            '13': '0x0874049f95d55fb76916262dc70571701b5c4cc5900c0691af75f1a8a52c8268',
            '14': '0x21d7212f3b4e5332fd465877b64926e3532653e2798a11255a46f533852dfe46',
            '15': '0x47b65307d0d654fd4f786b908c04af8fface7710fc998b37d219de19c39ee58c',
            '16': '0x66109972a14d82dbdb6894e61f74708f26128814b3359b64f8b66565679f7299',
            '17': '0x2eac15546def97adc6d69ca6e28eec831189baa2533e7910755d15403a0749e8',
            '18': '0x2e114163041d2fb8d45f9251db259a68ee6bdbfd6d10fe1ae87c5c4bcd6ba491',
            '19': '0xae9a2e131e9b359b198fa280de53ddbe2247730b881faae7af08e567e58915bd'})



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
            ({'to':       '0x0000000000000000000000000000000000000001',
              'value':    123,
              'gas':      132,
              'gasPrice': 123,
              'nonce':    123,
              'chainId':  1},
             "0xf85d7b7b81849400000000000000000000000000000000000000017b8025a091a4320e6ca6c34cb4645ab835fc164c3a3e28f657f2aa6bb3be1acd1a3008039f2fbd4fd1ebdcf2cda2b28a3f88e119e756535e0c1a421c2674482f2f30e89a")
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