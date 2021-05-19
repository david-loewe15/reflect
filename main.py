import locale

import requests
import argparse

from time import sleep

# Token Addresses
SAFEMOON_ADDRESS = "0x8076c74c5e3f5852037f31ff0093eeb8c8add8d3"

# API urls
BSCSCAN_API_ROOT = "https://api.bscscan.com/api"
TRANSACTIONS_URL = f"{BSCSCAN_API_ROOT}?module=account&action=tokentx"
BALANCE_URL = f"{BSCSCAN_API_ROOT}?module=account&action=tokenbalance"

parser = argparse.ArgumentParser(
    description="Calculate reflections given to a specific token address for the given contract"
)
parser.add_argument(
    "-c", "--contract", type=str, help="Contract address", required=True
)
parser.add_argument("-a", "--address", type=str, help="Wallet address", required=True)

locale.setlocale(locale.LC_NUMERIC, "en_us")

decimal = 0


def fetch_data(url):
    resp = requests.get(url)
    resp_json = resp.json()
    if "result" in resp_json:
        return resp_json["result"]
    else:
        return None


def get_total(contract_addr, wallet_addr):
    url = f"{BALANCE_URL}&contractaddress={contract_addr}&address={wallet_addr}"
    result = fetch_data(url)
    if result:
        return float(result) / pow(10, decimal)
    print("Not a valid address")
    exit(2)


def get_transactions(contract_addr, wallet_addr):
    url = f"{TRANSACTIONS_URL}&address={wallet_addr}"
    resp_json = fetch_data(url)
    result = []
    global decimal
    for record in resp_json:
        if "tokenDecimal" in record:
            decimal = int(record["tokenDecimal"])
        if (
            "value" in record
            and "tokenDecimal" in record
            and "contractAddress" in record
            and contract_addr == record["contractAddress"]
        ):
            result.append(float(record["value"]) / (pow(10, decimal)))
    if len(result):
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
    wallet_address = args.address
    contract_address = args.contract
    if contract_address.lower() == "safemoon":
        contract_address = SAFEMOON_ADDRESS

    transactions = get_transactions(contract_address, wallet_address)
    print("Waiting 5 seconds for rate limit\n")
    sleep(5)
    total = get_total(contract_address, wallet_address)

    coins_bought = sum_transactions(transactions)
    reflections_count = total - coins_bought

    formatted_total = format_value(total)
    formatted_coins = format_value(coins_bought)
    formatted_reflect = format_value(reflections_count)

    print(f"Results for wallet {wallet_address}")
    print(f"\tTotal Coins: {formatted_total.rjust(50 - len(formatted_total))}")
    print(f"-\tCoins bought:{formatted_coins.rjust(50 - len(formatted_coins))}")
    print(f"\tReflections:{formatted_reflect.rjust(50 - len(formatted_reflect))}")


if __name__ == "__main__":
    start()
