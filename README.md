# ShapeShift-cmd
[![Build Status](https://drone.io/github.com/PinIdea/shapeshift-cli/status.png)](https://drone.io/github.com/PinIdea/shapeshift-cli/latest)

Exchange cyrptocurrencies using command line with ShapeShift.io

#Dependencies:
Python3

# Usage

```
./shapeshift-cli.py <pair_to_exchange> <amount_to_be_exchanged> <wallet_cli>

EXAMPLES
		./shapeshift-cli.py DASH_BTC 1.5 dash-cli
	trade DASH for 1.5 BTC. use dash-cli
```

#Disclamer:
Don't use it if you want to exchange Coin/NXT or NXT/Coin. This script doen't support NXT yet.

If you want to see your transaction status within ShapeShift.io website, please visit this link after the generation of a deposit address:
https://shapeshift.io/txStat/ [generated deposit address]
