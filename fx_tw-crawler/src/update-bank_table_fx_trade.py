

import json
import argparse


if __name__ == '__main__':


    # args parse
    parser = argparse.ArgumentParser()

    parser.add_argument('--bank_fx_file')
    parser.add_argument('--bank_table')
    parser.add_argument('--out_file')

    args = parser.parse_args()


    # read input
    with open(args.bank_fx_file, 'r') as in_file :
        bank_fx_json_list = [ json.loads(line) for line in in_file ]

    with open(args.bank_table, 'r') as in_file:
        bank_table_json = json.load(in_file)


    # check and replace
    for fx_js in bank_fx_json_list:

        bank_id = fx_js['bank_id']

        for fx_key in fx_js['fx_table'].keys():

            if fx_js['fx_table'][fx_key]['bb_spot'] != '-':
                bank_table_json[bank_id]['fx_trade'][fx_key+'_SPOT'] = True
            else:
                bank_table_json[bank_id]['fx_trade'][fx_key+'_SPOT'] = False

            if fx_js['fx_table'][fx_key]['bb_cash'] != '-':
                bank_table_json[bank_id]['fx_trade'][fx_key+'_CASH'] = True
            else:
                bank_table_json[bank_id]['fx_trade'][fx_key+'_CASH'] = False


    # parse json and output
    parsed_json = json.dumps(bank_table_json, indent=4, sort_keys=False, ensure_ascii=False)

    with open(args.out_file, 'a') as out_file:
        out_file.write(parsed_json)
