import configparser
from pathlib import Path
from businesssearch import BusinessSearch
from queries import create_business_schema, create_business_table, insert_business_table
from databasedriver import DatabaseDriver
import argparse
import psycopg2

config = configparser.ConfigParser()
config.read_file(open(f"{Path(__file__).parents[0]}/config.cfg"))

parser = argparse.ArgumentParser(
        description="A Example yelp business finder based on parameters such as term, location, price, ")

api_key = config['KEYS']['API_KEY']
headers = {'Authorization': 'Bearer %s' % api_key}

def to_string(data):
    return [str(value) for value in data.values()]

def main():
    args = parser.parse_args()
    # Pricing levels to filter the search result with: 1 = $, 2 = $$, 3 = $$$, 4 = $$$$.
    b = BusinessSearch(term=args.term, location=args.location, price=args.price, limit=args.limit)
    db = DatabaseDriver()
    db.setup()   
    for offset in range(0, args.total, args.limit):
        for result in b.get_results(offset):
            values = to_string(result) 
            db.execute_upsert(values) 

if __name__ == "__main__":
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    required.add_argument("-t", "--term",  metavar='', required=True,
                          help="Search term, for example \"food\" or \"restaurants\". The term may also be business names, such as \"Starbucks.\".")
    required.add_argument("-l", "--location",  metavar='', required=True,
                          help="This string indicates the geographic area to be used when searching for businesses. ")
    optional.add_argument("-p", "--price", type=int, metavar='', required=False, default=1,
                          help="Pricing levels to filter the search result with: 1 = $, 2 = $$, 3 = $$$, 4 = $$$$.")
    optional.add_argument("--limit", type=int, required=False, default=20, help="limit of records retrieved by one request. ")
    optional.add_argument("--total", type=int, required=False, default=100, help="Upper bound on how many records retrieved in main. ")
    main()