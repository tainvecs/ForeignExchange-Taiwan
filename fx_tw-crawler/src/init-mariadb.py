

import argparse
import json
import pymysql
import re


DEBUG_MODE = True


def ParseArgs():

    parser = argparse.ArgumentParser()

    parser.add_argument('--mariadb_config')
    parser.add_argument('--mariadb_init_template')
    parser.add_argument('--bank_table')

    args = parser.parse_args()


    if DEBUG_MODE:

        print ("################## Arguments ##################")

        args_dict = vars(args)
        for key in args_dict:
            print ( "\t{}: {}".format(key, args_dict[key]) )

        print ("###############################################")

    return args


def __escape_str(string):

    if string is None:
        return 'None'
    else:
        return pymysql.escape_string(string)


if __name__ == '__main__':


    args = ParseArgs()

    # load input
    with open(args.mariadb_config, 'r') as in_json:
        mariadb_config = json.load(in_json)

    with open(args.mariadb_init_template, 'r') as in_json:
        mariadb_init_template = json.load(in_json)

    with open(args.bank_table, 'r') as in_json:
        bank_table = json.load(in_json)


    # connect to mysql
    conn_my = ( pymysql.connect(host=mariadb_config["mariadb_host"], port=mariadb_config["mariadb_port"], user=mariadb_config["mariadb_user"],
        password=mariadb_config["mariadb_password"], charset=mariadb_config["mariadb_charset"]) )

    cursor = conn_my.cursor()


    # create database
    database_name = '`{}`'.format(mariadb_config['mariadb_database'])
    cursor.execute("Create Database {};".format(database_name))
    cursor.execute("use {};".format(database_name))
    conn_my.commit()


    # generate bank_info table sql code
    sql_code = ''
    fx_list = list( bank_table[list(bank_table.keys())[0]]['fx_trade'].keys() )
    for line in mariadb_init_template['bank_info']:

        match = re.match(r'-- (.*)`(.*)`(.*)', line)

        if match:
            prefix, key_word, postfix = match.group(1,2,3)
            line_list = [ "{} `{}` {}".format(prefix.strip(), fx.strip(), postfix.rstrip(',').strip()) for fx in fx_list]
            line = ','.join(line_list)

        sql_code += line
    cursor.execute(sql_code)


    # generate bank table sql code
    for bank_id in bank_table:

        bank_js = bank_table[bank_id]

        # insert bank table information into bank_info
        click_xpaths = ", ".join(bank_js['click_xpaths'])

        fx_trade_str = []
        fx_trade = []
        for fx in fx_list:
            fx_trade_str.append(fx)
            if bank_js['fx_trade'][fx]:
                fx_trade.append('True')
            else:
                fx_trade.append('False')
        fx_trade_str = ', '.join(fx_trade_str)
        fx_trade = ', '.join(fx_trade)

        sql_str = r"INSERT INTO `{}` ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}) VALUES('{}', '{}', '{}', '{}', {}, {}, '{}', '{}', '{}', {});"
        sql_code = sql_str.format(
            'bank_info', 'bank_id', 'cn_name', 'en_name', 'start_link', 'js_spider',
            'fx_cycle', 'click_xpaths', 'last_updated_xpath', 'fx_table_xpath', fx_trade_str,
            __escape_str(bank_js['bank_id']),
            __escape_str(bank_js['cn_name']),
            __escape_str(bank_js['en_name']),
            __escape_str(bank_js['start_link']),
            bank_js['js_spider'],
            bank_js['fx_cycle'],
            __escape_str(click_xpaths),
            __escape_str(bank_js['last_updated_xpath']),
            __escape_str(bank_js['fx_table_xpath']),
            fx_trade
        )
        cursor.execute(sql_code)

        # create table for each bank
        sql_code = ""
        for line in mariadb_init_template['bank']:

            match = re.match(r'-- (.*)`(.*)`(.*)', line)

            if match:

                prefix, key_word, postfix = match.group(1,2,3)

                if key_word == 'BANK_ID':

                    line = "{} `{}` {}".format(prefix.strip(), bank_js['bank_id'].strip(), postfix.strip())

                elif key_word == 'FX':

                    line_list = []
                    for fx in bank_js['fx_trade']:
                        if bank_js['fx_trade'][fx]:
                            line_list.append("{} `{}` {}".format(prefix.strip(), fx.strip()+'_BB', postfix.rstrip(',').strip()))
                            line_list.append("{} `{}` {}".format(prefix.strip(), fx.strip()+'_BS', postfix.rstrip(',').strip()))
                    line = ','.join(line_list)

            sql_code += line
        cursor.execute(sql_code)


    conn_my.commit()

    cursor.close()
    conn_my.close()
