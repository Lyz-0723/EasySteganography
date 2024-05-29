import os

import gnupg


def check_path(path: str) -> str:
    return path if path[-1] == '/' else path + '/'


class GPG:
    def __init__(self, gpg_path: str, verbose: bool = False):
        self._gpg_path = check_path(gpg_path)
        self._gpg = gnupg.GPG(gnupghome=self._gpg_path, verbose=verbose)
        self._gpg.encoding = 'utf-8'

    def generate_key_pairs(self, output_path: str, passphrase: str) -> None:
        output_path = check_path(output_path)

        # generate the key
        key = self._gpg.gen_key(self._gpg.gen_key_input(key_type='RSA', key_length=1024, passphrase=passphrase))
        fp = key.fingerprint

        output_path += fp + '/'
        os.mkdir(output_path)

        output_path += fp

        # export the keys
        self._gpg.export_keys(fp, passphrase=passphrase, output=output_path + '_public_key.asc')
        self._gpg.export_keys(fp, True, passphrase=passphrase, output=output_path + '_private_key.asc')

        # delete the key from the keyring
        self.delete_keys(fp)

        # remove the key file
        key_path = self._gpg_path + 'openpgp-revocs.d/' + fp + '.rev'
        if os.path.exists(key_path):
            os.rename(key_path, output_path + '.rev')

    def delete_keys(self, fingerprint: str) -> None:
        self._gpg.delete_keys(fingerprint, True, ' ')
        self._gpg.delete_keys(fingerprint)

    def import_key(self, key_path: str) -> str:
        result = self._gpg.import_keys_file(key_path)

        fp = result.results[0]['fingerprint']
        self._gpg.trust_keys(fp, 'TRUST_ULTIMATE')
        return fp

    def encrypt_message(self, data: str, key_path: str) -> str:
        fp = self.import_key(key_path)
        cipher_text = self._gpg.encrypt(data, fp)

        self.delete_keys(fp)
        return str(cipher_text)

    def decrypt_message(self, data: str, key_path: str, passphrase: str) -> str:
        fp = self.import_key(key_path)
        plain_text = self._gpg.decrypt(data, passphrase=passphrase)

        self.delete_keys(fp)

        return str(plain_text)
