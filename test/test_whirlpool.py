# -*- coding: utf-8 -*-
import unittest

import whirlpool

from binascii import b2a_hex


data = {
    'empty'     : ''.encode('ascii'),
    'tqbfjotld' : 'The quick brown fox jumps over the lazy '
                  'dog'.encode('ascii'),
    'tqbfjotle' : 'The quick brown fox jumps over the lazy '
                  'eog'.encode('ascii'),
    'tqbf'      : 'The quick brown fox'.encode('ascii'),
    'jotld'     : ' jumps over the lazy dog'.encode('ascii'),
    'jotle'     : ' jumps over the lazy eog'.encode('ascii'),
    'unicode'   : u'ʯƝɨƈƟƉɛ'.encode('utf-8'),
    'binary'    : b'\xca\xaf\xc6\x9d\xc9\xa8\xc6\x88\xc6\x9f\xc6\x89\xc9\x9b',
}

results = {
    'empty'     : '19fa61d75522a4669b44e39c1d2e1726c530232130d'
                  '407f89afee0964997f7a73e83be698b288febcf88e3'
                  'e03c4f0757ea8964e59b63d93708b138cc42a66eb3',
    'tqbfjotld' : 'b97de512e91e3828b40d2b0fdce9ceb3c4a71f9bea8'
                  'd88e75c4fa854df36725fd2b52eb6544edcacd6f8be'
                  'ddfea403cb55ae31f03ad62a5ef54e42ee82c3fb35',
    'tqbfjotle' : 'c27ba124205f72e6847f3e19834f925cc666d097416'
                  '7af915bb462420ed40cc50900d85a1f923219d83235'
                  '7750492d5c143011a76988344c2635e69d06f2d38c',
    'tqbf'      : '317edc3c5172ea5987902aa9c4f1defedf4d5aa5920'
                  '9bdf7574cc6da0039852c24b8da70ecb07997ff83e8'
                  '6d32d2851215d3dcbd6bb9736bdef21c349d483e6d',
    'unicode'   : '2a083e3f53ddc2e4cd003104b0d020a9e7959188289'
                  'd39c5b58ac9478cbc7f429b851ddce0ca34a668b5f8'
                  '465175eb1b184afcf306da3afd5bd6f358c16257de',
    'binary'    : '2a083e3f53ddc2e4cd003104b0d020a9e7959188289'
                  'd39c5b58ac9478cbc7f429b851ddce0ca34a668b5f8'
                  '465175eb1b184afcf306da3afd5bd6f358c16257de',
}


def digest2hex(data):
    return b2a_hex(data).decode('ascii')


class TestWhirlpool(unittest.TestCase):

    def test_new_empty(self):
        wp = whirlpool.new()
        self.assertEqual(digest2hex(wp.digest()), results['empty'])
        self.assertEqual(wp.hexdigest(), results['empty'])

    def test_new_fox(self):
        wp1 = whirlpool.new(data['tqbfjotld'])
        self.assertEqual(digest2hex(wp1.digest()), results['tqbfjotld'])
        self.assertEqual(wp1.hexdigest(), results['tqbfjotld'])

        wp2 = whirlpool.new(data['tqbfjotle'])
        self.assertEqual(digest2hex(wp2.digest()), results['tqbfjotle'])
        self.assertEqual(wp2.hexdigest(), results['tqbfjotle'])

    def test_update_copy(self):
        wp1 = whirlpool.new()
        wp2 = wp1.copy()
        wp1.update(data['tqbf'])
        wp3 = wp1.copy()

        self.assertEqual(digest2hex(wp1.digest()), results['tqbf'])
        self.assertEqual(wp1.hexdigest(), results['tqbf'])

        self.assertEqual(digest2hex(wp2.digest()), results['empty'])
        self.assertEqual(wp2.hexdigest(), results['empty'])

        self.assertEqual(digest2hex(wp3.digest()), results['tqbf'])
        self.assertEqual(wp3.hexdigest(), results['tqbf'])

        wp1.update(data['jotld'])

        self.assertEqual(digest2hex(wp1.digest()), results['tqbfjotld'])
        self.assertEqual(wp1.hexdigest(), results['tqbfjotld'])

        self.assertEqual(digest2hex(wp2.digest()), results['empty'])
        self.assertEqual(wp2.hexdigest(), results['empty'])

        self.assertEqual(digest2hex(wp3.digest()), results['tqbf'])
        self.assertEqual(wp3.hexdigest(), results['tqbf'])

        wp3.update(data['jotle'])

        self.assertEqual(digest2hex(wp1.digest()), results['tqbfjotld'])
        self.assertEqual(wp1.hexdigest(), results['tqbfjotld'])

        self.assertEqual(digest2hex(wp2.digest()), results['empty'])
        self.assertEqual(wp2.hexdigest(), results['empty'])

        self.assertEqual(digest2hex(wp3.digest()), results['tqbfjotle'])
        self.assertEqual(wp3.hexdigest(), results['tqbfjotle'])

    def test_new_unicode(self):
        wp = whirlpool.new(data['unicode'])
        self.assertEqual(digest2hex(wp.digest()), results['unicode'])
        self.assertEqual(wp.hexdigest(), results['unicode'])

    def test_new_binary(self):
        wp = whirlpool.new(data['binary'])
        self.assertEqual(digest2hex(wp.digest()), results['binary'])
        self.assertEqual(wp.hexdigest(), results['binary'])

    def test_digest_size(self):
        wp = whirlpool.new()
        self.assertEqual(wp.digest_size, 64)
        with self.assertRaises((AttributeError, TypeError)):
            wp.digest_size = 32

    def test_block_size(self):
        wp = whirlpool.new()
        self.assertEqual(wp.block_size, 64)
        with self.assertRaises((AttributeError, TypeError)):
            wp.digest_size = 32


if __name__ == '__main__':
    unittest.main()
