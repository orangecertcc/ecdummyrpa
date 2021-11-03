#!/usr/bin/env python3

import argparse
import os

def gen_message(msg_filename, n):
    '''generate a message for signing given the name of the file'''

    message = f'Lorem ipsum dolor sit amet {n}'
    open(msg_filename, 'w').write(message)


def gen_signature(openssl_bin_path, privkey_filename, msg_filename, sig_filename, trace_filename, working_directory):
    '''Execute signature through tracergrind'''

    command = f'valgrind --tool=tracergrind --output={trace_filename} --trace-instr=no --trace-memread=yes --trace-memwrite=no {openssl_bin_path} dgst -sha256 -sign {privkey_filename} -out {sig_filename} {msg_filename}'
    os.system(command)


def gen_trace(trace_filename, w, bounds):
    '''Simulate a power trace from the read memory trace'''

    # apply Hamming weight model on the TracerGrind trace
    command = f'hwmemtrace {trace_filename} {trace_filename}.txt'    
    if not bounds is None:
        command += f' {bounds[0]} {bounds[1]}'
    os.system(command)
    
    # erase the original trace made by TracerGrind
    os.system(f'rm {trace_filename}')

    
def launch_simulation(openssl_bin_path, privkey_filename, working_directory, nsig, bounds, verb=False):
    if not working_directory.endswith('/'):
        working_directory += '/'

    if not os.path.exists(working_directory):
        os.mkdir(working_directory)
    if len(os.listdir(working_directory)) != 0:
        os.system('rm ' + working_directory + '/*')

    for n in range(nsig):
        print(f'Generating trace for signature {n + 1}/{nsig}')
        msg_filename = working_directory + f'message_{n}.txt'
        sig_filename = working_directory + f'signature_{n}.bin'
        trace_filename = working_directory + f'trace_{n}'
        gen_message(msg_filename, n)
        gen_signature(openssl_bin_path, privkey_filename, msg_filename, sig_filename, trace_filename, working_directory)
        gen_trace(trace_filename, 5, bounds)
        

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Power analysis simulation on OpenSSL')

    parser.add_argument('-b', action='store', dest='openssl_bin_path', type=str,
                        help='/path/to/openssl', required=True)

    parser.add_argument('--privkey', action='store', dest='privkey_filename', type=str,
                        help='/path/to/privatekey', required=True)

    parser.add_argument('--working-dir', action='store', dest='working_directory', type=str,
                        help='/path/to/working-directory', required=True)

    parser.add_argument('-n', action='store', dest='nsig', type=int,
                        help='Number of signatures to generate', required=True)

    parser.add_argument('--bounds', action='store', nargs = 2, dest='bounds', type=int,
                        required=False, default=None)
    
    args = parser.parse_args()    
    launch_simulation(args.openssl_bin_path, args.privkey_filename, args.working_directory, args.nsig, args.bounds, verb=True)
