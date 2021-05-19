# Reflect

Displays the number of reflections you have received for a BSC token using BscScan.com

The endpoint is rate-limited to 5 seconds per request as this project doesn't include an API Key for bscscan.com.

Requires Python 3.6+ and requests

## Usage

```
$ python main.py -h

usage: main.py [-h] -c CONTRACT -a ADDRESS

Calculate reflections given to a specific token address for the given contract

optional arguments:
  -h, --help            show this help message and exit
  -c CONTRACT, --contract CONTRACT
                        Contract address
  -a ADDRESS, --address ADDRESS
                        Wallet address
```

## Output

```
Results for wallet 0x12345...
	Total Coins:               123,456,789.12345
-	Coins bought:              112,345,678.90123
	Reflections:                11,111,110.22222
```
