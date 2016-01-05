import argparse

from stackquery.database import init_db


def init_argparse():
    parser = argparse.ArgumentParser(description='Database tools')
    parser.add_argument('--all', action='store_true',
                        help='Populate all tables', default=False)
    parser.add_argument('--projects', action='store_true',
                        help='Populate projects table')
    parser.add_argument('--release', action='store_true',
                        help='Populate release table')
    parser.add_argument('--user', action='store_true',
                        help='Populate user table')
    parser.add_argument('--team', action='store_true',
                        help='Populate team table', default=False)
    parser.add_argument('--report', action='store_true',
                        help='Populate report table')
    parser.add_argument('--filters', action='store_true',
                        help='Populate filters table')

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = init_argparse()
    init_db(args)
