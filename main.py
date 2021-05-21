import locale
from datetime import datetime

import requests
import argparse

from time import sleep

# Token Addresses
SAFEMOON_ADDRESS = "0x8076c74c5e3f5852037f31ff0093eeb8c8add8d3"
KISHU_INU_ADDRESS = "0xa2b4c0af19cc16a6cfacce81f192b024d625817d"
SHIBA_INU_ADDRESS = "0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce"
PANCAKESWAP_CAKE_ADDRESS = "0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82"

known_contracts = {
    SAFEMOON_ADDRESS: {"name": "Safemoon", "is_bsc": True},
    KISHU_INU_ADDRESS: {"name": "Kishu Inu", "is_bsc": False},
    SHIBA_INU_ADDRESS: {"name": "Shiba Inu", "is_bsc": False},
    PANCAKESWAP_CAKE_ADDRESS: {"name": "Pancakeswap CAKE", "is_bsc": True}
}

# API urls
BSCSCAN_API_ROOT = "https://api.bscscan.com/api"
ETHERSCAN_API_ROOT = "https://api.etherscan.io/api"

TRANSACTIONS_URL = f"?module=account&action=tokentx"
BALANCE_URL = f"?module=account&action=tokenbalance"
TOKENINFO_URL = f"{BSCSCAN_API_ROOT}?module=token&action=tokeninfo"


parser = argparse.ArgumentParser(
    description="Calculate reflections given to a specific token address for the given contract"
)
parser.add_argument(
    "-c", "--contract", type=str, help="Contract address", required=True
)
parser.add_argument("-a", "--address", type=str, help="Wallet address", required=True)
parser.add_argument("-e", "--etherscan", type=bool, nargs='?', const=True,
                    help="Use etherscan instead of bsc", default=False)

locale.setlocale(locale.LC_NUMERIC, "en_us")

decimal = 0

api_root = None

def fetch_data(url):
    resp = requests.get(url)
    resp_json = resp.json()
    if "result" in resp_json:
        return resp_json["result"]
    else:
        return None

def get_token_name(contract_address: str) -> str:
    url = f"{TOKENINFO_URL}&contractaddress={contract_address}"
    result = fetch_data(url)
    if result:
        return result['tokenName']
    else:
        print("Cannot get token name")
        exit(3)

def get_date(timestamp: str) -> str:
    return datetime.fromtimestamp(int(timestamp))

def get_total(contract_addr, wallet_addr):
    url = f"{api_root}{BALANCE_URL}&contractaddress={contract_addr}&address={wallet_addr}"
    result = fetch_data(url)
    if result:
        return float(result) / pow(10, decimal)
    print("Not a valid address")
    exit(2)


def get_transactions(contract_addr, wallet_addr):
    url = f"{api_root}{TRANSACTIONS_URL}&address={wallet_addr}"
    resp_json = fetch_data(url)
    result = ([], [])
    global decimal
    for record in resp_json:
        if "tokenDecimal" in record:
            decimal = int(record["tokenDecimal"])
        if (
            "value" in record
            and "tokenDecimal" in record
            and "contractAddress" in record
        ):
            float_value = float(record["value"]) / (pow(10, decimal))

            if contract_addr != record["contractAddress"]:
                # print(f"Transaction for {float_value} of contract {record['contractAddress']}, skipping")
                continue

            if record['to'] == wallet_addr:
                print(f"Value of {float_value} goes to this wallet on {get_date(record['timeStamp'])} ")
                result[0].append(float_value)
            elif record['from'] == wallet_addr:
                print(f"Value of {float_value} goes out of this wallet on {get_date(record['timeStamp'])} ")
                result[1].append(float_value)
            else:
                raise Exception("What just happened?")

    if len(result[0]) or len(result[1]):
        return result
    print("No valid transactions for wallet address")
    exit(1)


def sum_transactions(transactions):
    result: float = 0
    for transaction in transactions:
        result += transaction
    return result


def format_value(number):
    return locale.format_string("%f", number, grouping=True)


def start():
    args = parser.parse_args()
    wallet_address = args.address.lower()
    contract_address = args.contract

    global api_root

    if contract_address.lower() == "safemoon":
        contract_address = SAFEMOON_ADDRESS

    if contract_address.lower().startswith('kishu'):
        contract_address = KISHU_INU_ADDRESS

    if contract_address.lower().startswith('shib'):
        contract_address = SHIBA_INU_ADDRESS

    if contract_address.lower().startswith('cake'):
        contract_address = PANCAKESWAP_CAKE_ADDRESS

    use_etherscan = args.etherscan
    token_name = None

    if contract_address in known_contracts:
        use_etherscan = not known_contracts[contract_address]["is_bsc"]
        token_name = known_contracts[contract_address]["name"]

    if use_etherscan:
        print("Using ERC-20 network")
        api_root = ETHERSCAN_API_ROOT
    else:
        print("Using BSC network")
        api_root = BSCSCAN_API_ROOT


    print(f"Checking transactions for wallet {wallet_address}")

    if token_name:
        print(f"Checking transactions for contract {contract_address} (name: {token_name})")
    else:
        print(f"Checking transactions for contract {contract_address}")

    transactions = get_transactions(contract_address, wallet_address)
    print("Waiting 5 seconds for rate limit\n")
    sleep(5)
    total = get_total(contract_address, wallet_address)

    coins_bought = sum_transactions(transactions[0])
    coins_sold = sum_transactions(transactions[1])

    net = coins_bought - coins_sold

    reflections_count = total - net

    formatted_total = format_value(total)

    formatted_coins_bought = format_value(coins_bought)
    formatted_coins_sold = format_value(coins_sold)

    formatted_reflect = format_value(reflections_count)

    print(f"Results for wallet {wallet_address}")
    print(f"\tTotal Coins: {formatted_total.rjust(50 - len(formatted_total))}")
    print(f"-\tCoins bought:{formatted_coins_bought.rjust(50 - len(formatted_coins_bought))}")
    print(f"-\tCoins sold:{formatted_coins_sold.rjust(50 - len(formatted_coins_sold))}")
    print(f"\tReflections:{formatted_reflect.rjust(50 - len(formatted_reflect))}")


if __name__ == "__main__":
    start()
