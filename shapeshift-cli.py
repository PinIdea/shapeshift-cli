#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ShapeShift-cmd : Exchanging cryptocurrencies using command line with Shapeshift.io
#
# Copyright © 2016 Chiheb Nexus
# Copyright © 2017 Tomasen
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
##########################################################################

from urllib.request import urlopen, Request
from json import loads, dumps
from subprocess import call
import time
import math
import sys
import argparse


class ShapeShiftCmd:
    """
    """

    def __init__(self):
        """
        """

        self.url_rate = "https://shapeshift.io/rate/"
        self.url_limit = "https://shapeshift.io/limit/"
        self.url_market = "https://shapeshift.io/marketinfo/"
        self.url_coins = "https://shapeshift.io/getcoins"
        self.url_valid_address = "https://shapeshift.io/validateAddress/"
        self.url_post_exchange = "https://shapeshift.io/shift/"
        self.url_tx_status = "https://shapeshift.io/txStat/"
        self.url_send_amount = "https://shapeshift.io/sendamount"

        self.pair = ""

    def safe_exit(self):
        """
        """
        sys.exit(0)

    def run(self):
        """
        """
        coins, pairs, coins_name, coins_symbols = [], [], [], []
        pair_to_exchange, withdraw_address, deposit_address, refund_address = "", "", "", ""

        parser = argparse.ArgumentParser(
            description='exchange cryptocurrencies using command line interface with ShapeShift.io')
        parser.add_argument('-y', action='store_true', dest='skip_confirmation', default=False,
                            help='attempt to proceed without prompting for confirmation')
        parser.add_argument('pair_to_exchange', type=str,
                            help="what coins are being exchanged in the form [input coin]_[output coin]  ie DASH_BTC")
        parser.add_argument('withdraw_address', type=str,
                            help="the address for resulting coin to be sent to")
        parser.add_argument('refund_address', type=str,
                            help="address to return deposit to if anything goes wrong with exchange")
        parser.add_argument('amount_to_be_exchanged', type=float,
                            help='the amount to be sent to the withdrawal address')
        parser.add_argument('wallet_cli', type=str, nargs='?',
                            help="the path or executable command of your wallet client, such as: dash-cli bitcoin-cli")

        args = parser.parse_args()

        pair_to_exchange = args.pair_to_exchange
        withdraw_address = args.withdraw_address
        refund_address = args.refund_address
        amount_to_be_exchanged = args.amount_to_be_exchanged
        wallet_cli = args.wallet_cli
        skip_confirmation = args.skip_confirmation

        while True:
            try:
                if self.validate_address(self.url_valid_address, withdraw_address, pair_to_exchange.split("_")[1]):
                    print(" |-> Your withdraw address is valid")
                    break
                else:
                    print("Enter a valid {0} address".format(
                        pair_to_exchange.split("_")[1]))
            except Exception as ex:
                print("Cannot validate your withdraw address.\nProgram will exit")
                self.safe_exit()

        #  double check withdraw_address
        if not skip_confirmation and not self.query_yes_no('the resulting coin to be sent to \x1B[33;10m{0}\x1B[0m'
                                                           .format(withdraw_address), "no"):
            self.safe_exit()

        while True:
            try:
                if refund_address == "":
                    refund_address = None
                    break
                if self.validate_address(self.url_valid_address, refund_address, pair_to_exchange.split("_")[0]):
                    print(" |-> Your refund address is valid")
                    break
                else:
                    print("Enter a valid {0} address".format(
                        pair_to_exchange.split("_")[0]))
            except Exception as ex:
                print("Cannot validate your refund address.\nProgram will exit")

        # double check refund_address
        if not skip_confirmation and not self.query_yes_no('if anything goes wrong with exchange,' +
                                                           'your deposit will be sent to \x1B[33;10m{0}\x1B[0m'
                                                           .format(withdraw_address), "no"):
            self.safe_exit()

        # print market price and deposit limit
        try:
            print("[+] Printing ShapeShift.io market price for {0}/{1}".format(pair_to_exchange.split("_")[0],
                                                                               pair_to_exchange.split("_")[1]))
            rate, limit_deposit, min_deposit, miner_fees, max_limit = self.return_market_info(
                self.url_market, pair_to_exchange)
            print(" |\t\t {0}/{1}".format(pair_to_exchange.split("_")
                                          [0], pair_to_exchange.split("_")[1]))
            print(" ---------------------------------------------------")
            print(" | Rate \t\t:\t{0}".format(rate))
            print(" | Limit(Quick)  \t:\t{0}".format(limit_deposit))
            print(" | Limit(Precise)  \t:\t{0}".format(max_limit))
            print(" | Deposit minimum\t:\t{0}".format(min_deposit))
            print(" | Miner fees     \t:\t{0}".format(miner_fees))
            print(" ---------------------------------------------------")
        except Exception as ex:
            print("Cannot print ShapeShift.io market for pairs")
            print("Program will exit")
            self.safe_exit()

        safe_amount_to_be_exchanged_each_time = math.floor(
            max_limit * rate * 900) / 1000

        while True:
            try:

                amount_of_this_round = amount_to_be_exchanged

                if amount_of_this_round / rate <= min_deposit:
                    print(" |-> {0} less than minimum requirement:{1}"
                          .format(amount_to_be_exchanged, min_deposit))
                    break

                if safe_amount_to_be_exchanged_each_time < amount_to_be_exchanged:
                    amount_of_this_round = safe_amount_to_be_exchanged_each_time

                print("[+] {1} left to be aqquired. initiate transaction for {0} this round."
                      .format(amount_of_this_round, amount_to_be_exchanged))

                deposit_address, deposit_amount, depositType = \
                    self.post_exchange_request(self.url_send_amount, pair_to_exchange,
                                               withdraw_address, amount_of_this_round,
                                               refund_address)

                print(" ---------------------------------------------------")
                # check wallet cli existense
                if wallet_cli is not None:
                    print(
                        " | Excuting: {2} sendtoaddress \"{0}\" {1}".format(deposit_address, deposit_amount, wallet_cli))
                    ret = call([wallet_cli, "sendtoaddress",
                                deposit_address, deposit_amount])
                    if ret != 0:
                        if ret < 0:
                            print("Killed by signal", -ret)
                        else:
                            print("Command failed with return code", ret)
                    else:
                        print("SUCCESS!!")
                else:
                    print("[+] Please deposit \x1B[31;10m{2}\x1B[0m {1} to this address:\t \x1B[31;10m{0}\x1B[0m"
                          .format(deposit_address, depositType, deposit_amount))

                print(" ---------------------------------------------------")
                amount_already_sent = self.transaction_status(
                    self.url_tx_status, deposit_address)
                if amount_already_sent is not None:
                    amount_to_be_exchanged -= amount_already_sent
                else:
                    break

            except Exception as ex:
                print("Error: " + ex)
                print("Cannot figure the transaction status.\nProgram will exit")
                self.safe_exit()

    def check_valid_pair(self, u_input, u_exchange, pairs):
        """
        """
        if u_input + "_" + u_exchange in pairs:
            return True
        else:
            return False

    def user_input(self, u_input, coins_symbols):
        """
        """
        if u_input in coins_symbols:
            return True
        else:
            return False

    def print_coins_symbols(self, coins):
        """
        """
        coins_name, coins_symbols = [], []
        for i in coins:
            coins_name.append(i[0])
            coins_symbols.append(i[1])

        print("|   Coin name    :   Coin symbol")
        for j in coins:
            print("----------------------------------------")
            print("|   {0}{1}:\t  {2}".format(
                j[0], (13 - len(j[0])) * " ", j[1]))
        print("----------------------------------------")

        return coins_name, coins_symbols

    def load_url_data(self, url):
        """
        """
        response = urlopen(url)
        content = response.read()
        data = loads(content.decode("UTF-8"))

        return data

    def return_avaible_coins(self, url):
        """
        """
        data = self.load_url_data(url)
        coins = []
        for i in data:
            if data[i]["status"] == "available":
                coins.append([data[i]["name"], data[i]["symbol"]])
            else:
                pass

        return coins

    def return_pairs(self, url):
        """
        """
        data = self.load_url_data(url)
        pairs = []

        for i in data:
            if "SHAPESHIFTCD" in i["pair"]:
                pass
            else:
                pairs.append(i["pair"])

        return pairs

    def return_market_info(self, url, pair):
        """
        """
        data = self.load_url_data(url + pair)

        return data["rate"], data["limit"], data["minimum"], data["minerFee"], data["maxLimit"]

    def return_deposit_limit(self, url, pair):
        """
        """
        data = self.load_url_data(url + pair)
        limit = data["limit"]

        return limit

    def validate_address(self, url, address, coin):
        """
        """
        data = self.load_url_data(url + address + "/" + coin)

        return data["isvalid"]

    def post_exchange_request(self, url, pair, withdraw_add, amount, return_address=None,
                              dest_tag=None, rs_address=None):
        """
        """
        depositType, withdrawType = pair.split("_")

        post_data = {"pair": pair, "withdrawal": withdraw_add, "returnAddress": return_address,
                     "destTag": dest_tag, "rsAdress": rs_address, "amount": amount,
                     "apiKey": "6a76627d7b5418277b431f6dd2b4c2e01a4db6fccd2dcc4b9545f82c7e314" +
                     "5d3e666517a76d884354a3815ddb9ee85f19e77bfc14cc9a83a968a218dd36d58fc"}

        json_data = dumps(post_data).encode("UTF-8")
        request = Request(url, data=json_data, headers={
            'Content-Type': 'application/json'})

        response = urlopen(request)
        content = response.read()

        data_o = loads(content.decode("UTF-8"))
        data = data_o["success"]

        print(" | Deposit \x1B[31;10m{0}\x1B[0m {1} to this address:\t \x1B[31;10m{2}\x1B[0m,".format(
            data["depositAmount"], depositType, data["deposit"]))

        print(" | Your \x1B[33;10m{0}\x1B[0m {1} will be send to this address:\t \x1B[37;10m{2}\x1B[0m".format(
            data["withdrawalAmount"], withdrawType, data["withdrawal"]))
        if return_address is not None:
            print(" | Your {0} refund address is:\t\t \x1B[37;10m{1}\x1B[0m".format(
                depositType, return_address))

        return data["deposit"], data["depositAmount"], depositType

    def transaction_status(self, url, address):
        """
        """
        sleeping_time_sec = 0

        while True:
            data = self.load_url_data(url + address)

            if data["status"] == "no_deposits":
                if sleeping_time_sec == 600:
                    print("\nExit with status: ", data["status"])
                    break

                remaning_sec = 600 - sleeping_time_sec
                m, s = divmod(remaning_sec, 60)
                remaning_minutes = "%02d:%02d" % (m, s)
                msg = r' | Waiting the deposit to this address: {0}			ETA: {1}'.format(
                    data["address"], remaning_minutes)
                print("\r{0}".format(msg), end="")

            elif data["status"] == "received":
                msg = r' | We see a new deposit but we have not finished it!. Please wait...{0}'.format(
                    44 * " ")
                print("\r{0}".format(msg), end="")

            elif data["status"] == "complete":
                print("\n |-> Transaction complete!")
                print("[-] You've made a deposit to this address: {0}\n\
[-] Withdrawal address: {1}\n\
[-] You've desposit: {2}{3}\n\
[-] You'll have: {4}{5}\n\
[-] Transaction ID: {6}".format(data["address"], data["withdraw"], data["incomingCoin"],
                                data["incomingType"], data["outgoingCoin"], data["outgoingType"], data["transaction"]))
                return float(data["outgoingCoin"])
                break
            else:
                print("[-] unknown transaction status:", data["status"])

            sleeping_time_sec += 5
            time.sleep(5)

    def query_yes_no(self, question, default="yes"):
        """Ask a yes/no question via raw_input() and return their answer.

        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

        The "answer" return value is True for "yes" or False for "no".
        """
        valid = {"yes": True, "y": True, "ye": True,
                 "no": False, "n": False}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)

        while True:
            print(question + prompt)
            choice = input().lower()
            if default is not None and choice == '':
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write("Please respond with 'yes' or 'no' "
                                 "(or 'y' or 'n').\n")


if __name__ == '__main__':
    app = ShapeShiftCmd()
    app.run()
