# shapeshift-cli

Exchange cyrptocurrencies using command line interface with ShapeShift.io

#Dependencies:

Python3

# Usage

```
usage: shapeshift-cli.py [-h] [-y]
                         pair_to_exchange withdraw_address refund_address
                         amount_to_be_sent [wallet_cli]

exchange cyrptocurrencies using command line interface with ShapeShift.io

positional arguments:
  pair_to_exchange   what coins are being exchanged in the form [input
                     coin]_[output coin] ie DASH_BTC
  withdraw_address   the address for resulting coin to be sent to
  refund_address     address to return deposit to if anything goes wrong with
                     exchange
  amount_to_be_sent  the amount to be sent to the withdrawal address
  wallet_cli         the path or the executable command of your wallet client,
                     such as: dash-cli bitcoin-cli

optional arguments:
  -h, --help         show this help message and exit
  -y                 attempt to proceed without prompting for

EXAMPLES
		./shapeshift-cli.py DASH_BTC <withdraw_address> <refund_address> 1.5 dash-cli
		trade DASH for 1.5 BTC. use dash-cli
```

- Trade amount larger than max deposit limit will be automatically split to separated
and rather small transactions that within shapeshift's limits.

#Disclamer:

Don't use it if you want to exchange Coin/NXT or NXT/Coin. This script doen't support NXT yet.

If you want to see your transaction status within ShapeShift.io website, please visit this link after the generation of a deposit address:
https://shapeshift.io/txStat/ [generated deposit address]
