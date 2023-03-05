#!/usr/bin/env python3

import base64
import datetime
import os
import random
import sys

import qrcode
import requests
from rich import print as rprint
from rich.progress import track

# URLs for configs not encoded in a base64 string
DECODED_URLS = [
    "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all",
]

# URLs for configs encoded in a base64 string
ENCODED_URLS = [
    "https://raw.githubusercontent.com/freefq/free/master/v2",
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
    "https://raw.githubusercontent.com/AzadNetCH/Clash/main/V2Ray.txt",
    "https://raw.githubusercontent.com/vpei/Free-Node-Merge/main/o/node.txt",
    "https://raw.githubusercontent.com/tbbatbb/Proxy/master/dist/v2ray.config.txt",
    "https://raw.fastgit.org/ripaojiedian/freenode/main/sub",
    "https://github.xiaoku666.tk/https://raw.githubusercontent.com/ripaojiedian/freenode/main/sub",
    "https://raw.githubusercontent.com/learnhard-cn/free_proxy_ss/main/v2ray/v2raysub",
]
COLORS = ["red", "green", "yellow", "blue", "magenta", "cyan", "white"]
NOW = datetime.datetime.now()
QR_DIR = "./qr_codes"


def get_config(url):
    """Get config from URL."""

    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


def decode_base64(string):
    """Decode base64 encoded string."""

    try:
        decoded_string = base64.b64decode(string).decode()
        return decoded_string
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_cleaned_configs(vmess=False):
    """Get cleaned configs."""

    # Get all configs
    configs = []
    all_urls = DECODED_URLS + ENCODED_URLS
    for url in track(all_urls, description="Getting configs..."):
        if url in DECODED_URLS:
            config = get_config(url)
            if config:
                configs.extend(config.splitlines())
        elif url in ENCODED_URLS:
            decoded_config = decode_base64(get_config(url))
            if decoded_config:
                configs.extend(decoded_config.splitlines())

    if vmess:
        configs = [config for config in configs if "vmess" in config]

    return configs


# download and save the configs
def save_configs(configs):
    """Save configs to file."""

    file_name = f"./configs_{NOW.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write("\n".join(configs))
    rprint(f"[bold green]Config file saved to {file_name}[/bold green]")


# get random color for the config
def get_random_color(word):
    """Returns a random color wrapped around the given word."""

    random_color = random.choice(COLORS)
    return f"[{random_color}]{word}[{random_color}]"


# generate some random configs, default 5
def get_random_config(configs, random_configs=5):
    """Returns a list of random configs from the given list of whole configs."""

    random_configs = random.sample(configs, random_configs)
    return random_configs


def save_qr_code(data):
    """Save QR codes to qr_codes directory."""

    for index, qr_data in enumerate(data, start=1):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        if not os.path.exists(QR_DIR):
            os.makedirs(QR_DIR)

        img = qr.make_image(fill_color="black", back_color="white")
        file_name = f"{QR_DIR}/{str(index).zfill(0000)}_qr_code_{NOW.strftime('%Y-%m-%d_%H-%M-%S')}.png"
        img.save(file_name)

    # Display the number of QR codes saved
    rprint(
        f"[bold yellow]{len(data)} QR code(s) saved to qr_codes directory.[/bold yellow]"
    )


def main():
    """Main function."""

    # Display usage message if no options are provided
    if len(sys.argv) == 1:
        rprint("[bold red]Usage: python3 main.py [OPTIONS][/bold red]")
        rprint("[bold red]Options:[/bold red]")
        rprint("[bold red]-n, --number[/bold red]\t[green]Number of configs[/green]")
        rprint(
            "[bold red]-v, --vmess[/bold red]\t[green]Get vmess configs only[/green]"
        )
        rprint("[bold red]-s, --save[/bold red]\t[green]Save configs to a file[/green]")
        rprint("[bold red]-q, --qr[/bold red]\t[green]Save QR codes[/green]")
        sys.exit(1)

    # Get vmess configs only
    if "-v" in sys.argv or "--vmess" in sys.argv:
        configs = get_cleaned_configs(vmess=True)
    else:
        configs = get_cleaned_configs()

    # Display the number of configs downloaded
    configs_length = len(configs)
    rprint(f"[bold yellow]{configs_length} configs downloaded.[/bold yellow]\n")

    # Exit if no configs are found
    if configs_length == 0:
        rprint("[bold red]No configs found.[/bold red]")
        sys.exit(1)

    # Get random configs
    if "-n" in sys.argv or "--number" in sys.argv:
        try:
            config_number = int(sys.argv[sys.argv.index("-n") + 1])
        except ValueError:
            try:
                config_number = int(sys.argv[sys.argv.index("--number") + 1])
            except ValueError:
                config_number = 5
        if config_number > configs_length:
            config_number = configs_length

        random_configs = get_random_config(configs, config_number)

        # Print random configs with random colors
        if "--silent" not in sys.argv:
            for config in random_configs:
                rprint(get_random_color(config))
                rprint("")

        # Save configs to a file
        if "-s" in sys.argv or "--save" in sys.argv:
            save_configs(random_configs)

        # Save QR codes
        if "-q" in sys.argv or "--qr" in sys.argv:
            save_qr_code(random_configs)

        # Display the number of random configs generated
        rprint(f"[bold yellow]{config_number} random configs generated.[/bold yellow]")


if __name__ == "__main__":
    main()
