# kaliban.py -u url
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Kaliban web scanner')
    parser.add_argument('-u', type=str, default=None, dest="url", help='Target url')
    parser.add_argument('-o', type=str, default='result', dest="out", help='Output file')
    parser.add_argument('-l', type=str, default=None, dest="input_file", help='File with url list')
    parser.add_argument('-ua', type=str, default=None, dest="user_agent", help='Set custom user-agent')
    parser.add_argument('-proxy', type=str, default=None, dest="proxy", help='Set proxy in format 127.0.0.1:8080')
    parser.add_argument('-sub', action='store_true', default=False, dest="sub_on", help='Find subdomain')
    parser.add_argument('-interest', action='store_true', default=False, dest="int_on", help='Find interesting file')

    args = parser.parse_args()

    if (args.url is None) and (args.input_file is None):
        print('No target specified. Use -h for help')
        raise Exception('No target specified')
    return args
