

import argparse
import json


if __name__ == '__main__':


    # args parse
    parser = argparse.ArgumentParser()

    parser.add_argument('--bank_table')
    parser.add_argument('--bank_table_min')
    parser.add_argument('--bank_table_day')

    args = parser.parse_args()


    # input
    with open(args.bank_table, 'r') as in_file:
        bank_table = json.load(in_file)


    # split
    bank_table_min = {}
    bank_table_day = {}
    for bank_id in bank_table:

        bank = bank_table[bank_id]

        if bank['fx_cycle'] == 10:
            bank_table_min[bank_id] = bank
        elif bank['fx_cycle'] == 1440:
            bank_table_day[bank_id] = bank
        else:
            raise


    # output
    with open(args.bank_table_min, 'w') as out_file:
        out_file.write(json.dumps(bank_table_min, indent=4, sort_keys=False, ensure_ascii=False))

    with open(args.bank_table_day, 'w') as out_file:
        out_file.write(json.dumps(bank_table_day, indent=4, sort_keys=False, ensure_ascii=False))
