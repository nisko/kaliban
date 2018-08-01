from source.args_parser import parse_args
from source.kaliban import Kaliban


if __name__ == '__main__':
    args = parse_args()
    kaliban = Kaliban(args)
    kaliban.start()
