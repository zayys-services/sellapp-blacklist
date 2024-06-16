import threading
import requests
import traceback
import json
import time
import os
from colorama import Fore, init
from requests.exceptions import ProxyError, ConnectionError, Timeout, RequestException, HTTPError
from ratelimit import limits, sleep_and_retry
from urllib3.exceptions import MaxRetryError, NewConnectionError

os.system('title https://zayy.pro  Zayys Services  Sell.app Blacklister')

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Global variables
SELL_APP_API_KEY = None
debug = False  # Default debug mode off
blacklist_option = None
blacklist_directory = None

# Function to read configuration from config.json
def read_config():
    config_file = 'config.json'
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        if config.get('debug_mode', False):
            print(Fore.GREEN + f"Config file '{config_file}' successfully read.")
        return config
    except FileNotFoundError:
        print(Fore.RED + f"Config file '{config_file}' not found.")
    except json.JSONDecodeError as e:
        print(Fore.RED + f"Failed to decode JSON in config file: {e}")
    except Exception as e:
        print(Fore.RED + f"Failed to read config file: {e}")
    return None

# Function to initialize configuration and SELL_APP_API_KEY
def initialize_config():
    global SELL_APP_API_KEY, debug

    # Read configuration
    config = read_config()
    if config is None:
        return False

    SELL_APP_API_KEY = config.get('sell_app_api_key')  # Corrected key name
    debug = config.get('debug_mode', False)

    return True

# Function to read domains from a file
def read_domains(filename):
    try:
        with open(filename, 'r') as file:
            domains = file.read().splitlines()
        if debug:
            print(Fore.GREEN + f"Domains successfully read from '{filename}'.")
        return domains
    except FileNotFoundError:
        print(Fore.RED + f"Domains file '{filename}' not found.")
    except Exception as e:
        print(Fore.RED + f"Failed to read domains from '{filename}': {e}")
    return None

# Function to read proxies from a file
def read_proxies(filename):
    try:
        with open(filename, 'r') as file:
            proxies = file.read().splitlines()
        if debug:
            print(Fore.GREEN + f"Proxies successfully read from '{filename}'.")
        return proxies
    except FileNotFoundError:
        print(Fore.RED + f"Proxies file '{filename}' not found.")
    except Exception as e:
        print(Fore.RED + f"Failed to read proxies from '{filename}': {e}")
    return None

def spacer():
    print("   ")
    print("   ")
    print("   ")

# Function to add a domain to the blacklist
@sleep_and_retry
@limits(calls=50, period=160)  # 5 calls per 60 seconds
def add_domain_to_blacklist(domain, proxy, processed_domains, processed_domains_lock, debug):
    global SELL_APP_API_KEY, blacklist_option
    
    # Print API key and blacklist option
    print(Fore.GREEN + f"Sell.app API Key: {SELL_APP_API_KEY}")
    print(Fore.GREEN + f"Blacklist Option: {blacklist_option}")

    url = 'https://sell.app/api/v1/blacklists'
    headers = {
        'Authorization': f"Bearer {SELL_APP_API_KEY}",
        'Content-Type': 'application/json',
        'accept': 'application/json'
    }
    payload = {
        "type": blacklist_option,
        "data": f"{domain}",
        "description": f"Blacklist rule for {domain}"
    }

    proxy_dict = {
        'http': f'http://{proxy}',
        'https': f'http://{proxy}'
    }

    try:
        print(Fore.BLUE + f"Attempting to add domain {domain} using proxy {proxy}.")
        response = requests.post(url, json=payload, headers=headers, proxies=proxy_dict, timeout=10)
        response.raise_for_status()

        if response.status_code == 201:
            print(Fore.GREEN + f"Successfully added domain {domain} to blacklist. Status code: {response.status_code}")
            spacer()
            with processed_domains_lock:
                processed_domains.add(domain)
        elif response.status_code == 422:
            print(Fore.YELLOW + f"The domain {domain} has already been blacklisted, skipping...")
            spacer()
            with processed_domains_lock:
                processed_domains.add(domain)
        elif response.status_code == 402:
            print(Fore.RED + f"Failed to add domain {domain} to blacklist. Payment required. Status code: {response.status_code}")
            spacer()
        else:
            print(Fore.RED + f"Unexpected response for domain {domain}: {response.status_code}. Error: {response.text}")
            spacer()

    except HTTPError as e:
        handle_http_error(e, domain, processed_domains, processed_domains_lock, response)
    except ConnectionError as e:
        handle_connection_error(e, url, proxy)
    except (ProxyError, Timeout, RequestException, MaxRetryError, NewConnectionError) as e:
        handle_request_exception(e, domain, proxy)
    except Exception as e:
        print(Fore.RED + f"An unexpected error occurred for domain {domain}: {type(e).__name__}: {str(e)}.")
        spacer()

    return True

# Exception handlers
def handle_http_error(e, domain, processed_domains, processed_domains_lock, response):
    global debug

    if e.response.status_code == 422:
        print(Fore.YELLOW + f"The domain {domain} has already been blacklisted, skipping...")
        spacer()
    elif response.status_code == 201:
        print(Fore.GREEN + f"Successfully added domain {domain} to blacklist. Status code: {response.status_code}")
        spacer()
        with processed_domains_lock:
            processed_domains.add(domain)
    elif e.response.status_code == 429:
        print(Fore.YELLOW + f"Too many requests. Changing proxy and retrying...")
        spacer()
    else:
        print(Fore.RED + f"HTTP error occurred for domain {domain}: {e}")
        spacer()

def handle_connection_error(e, url, proxy):

    if 'RemoteDisconnected' in str(e):
        print(Fore.YELLOW + f"Connection aborted. RemoteDisconnected. Changing proxy and retrying...")
        spacer()  # Call the spacer function
        time.sleep(2)
    else:
        print(Fore.RED + f"Failed to connect to {url} using proxy {proxy}. Exception: {type(e).__name__}: {str(e)}.")

def handle_request_exception(e, domain, proxy):
    print(Fore.RED + f"Failed to process {domain} using proxy {proxy}. Exception: {type(e).__name__}: {str(e)}.")
    spacer()
# Worker function for threading
def worker(domains, proxies, blacklist_rules, processed_domains, processed_domains_lock, debug):
    try:
        for domain in domains:
            if domain not in blacklist_rules and domain not in processed_domains:
                proxy_index = 0
                success = False
                while not success and proxy_index < len(proxies):
                    proxy = proxies[proxy_index]
                    success = add_domain_to_blacklist(domain, proxy, processed_domains, processed_domains_lock, debug)
                    proxy_index += 1
                if not success:
                    print(Fore.RED + f"All proxies exhausted for domain {domain}. Skipping...")
            else:
                print(Fore.YELLOW + f"The domain {domain} is already blacklisted or processed, skipping...")
    except Exception as e:
        print(Fore.RED + f"Exception in thread {threading.current_thread().name}: {e}")

def main():
    global SELL_APP_API_KEY, blacklist_option, blacklist_directory, debug

    # Initialize configuration
    if not initialize_config():
        return

    # Set blacklist option and directory through menu
    if debug:
        print(Fore.GREEN + f"Starting menu setup.")
    show_menu()

    # Read domains from selected blacklist file
    if blacklist_directory:
        domains_file = read_domains(blacklist_directory)
        if domains_file is None:
            return
    else:
        print(Fore.RED + "No blacklist directory specified.")
        return

    # Read proxies from file
    proxies_file = "./data/proxies.txt"
    proxies = read_proxies(proxies_file)
    if proxies is None:
        return

    # Initialize processed_domains set and a lock for thread-safe access
    processed_domains = set()
    processed_domains_lock = threading.Lock()

    # Determine number of threads to use
    config = read_config()  # Re-reading config to get 'threads' value
    if config is None:
        return

    threads_to_use = config.get('threads', 10)  # Default to 10 if not specified
    if isinstance(threads_to_use, int) and threads_to_use > 0:
        if debug:
            print(Fore.GREEN + f"Using {threads_to_use} threads to process {len(domains_file)} domains with {len(proxies)} proxies.")
    else:
        print(Fore.RED + "Invalid 'threads' value in config.json. Using default value (10)...")
        threads_to_use = 10  # Default value

    # Start worker threads
    threads = []
    for i in range(min(threads_to_use, len(domains_file))):
        thread = threading.Thread(target=worker, args=(domains_file, proxies, config.get('blacklist_rules', []), processed_domains, processed_domains_lock, debug))
        threads.append(thread)
        thread.start()
        if debug:
            print(Fore.GREEN + f"Started thread {thread.name}.")

    # Wait for all threads to complete
    for thread in threads:
        thread.join()
        if debug:
            print(Fore.GREEN + f"Thread {thread.name} completed.")

# Menu function to select blacklist option
menu_options = {
    '1': Fore.CYAN + "Wildcard Emails",
    '2': Fore.CYAN + "IP Addresses",
    '3': Fore.CYAN + "Emails",
    '4': Fore.CYAN + "Countries",
    '5': Fore.CYAN + "ASNs",
    '6': Fore.RED + "Exit"
}

def show_menu():
    global blacklist_option, blacklist_directory, debug
    if debug:
        print(Fore.GREEN + f"Setting up menu...")

    os.system("CLS")
    print("  ")
    print(Fore.YELLOW + """8888888888P                                8888888b.                  
      d88P                                 888   Y88b                 
     d88P                                  888    888                 
    d88P     8888b.  888  888 888  888     888   d88P 888d888 .d88b.  
   d88P         "88b 888  888 888  888     8888888P"  888P"  d88""88b 
  d88P      .d888888 888  888 888  888     888        888    888  888 
 d88P       888  888 Y88b 888 Y88b 888     888        888    Y88..88P 
d8888888888 "Y888888  "Y88888  "Y88888     888        888     "Y88P"  
                          888      888                              
                     Y8b d88P  Y8b d88P                              
                      "Y88P"    "Y88P"                               
                                                                      
""")
    print(Fore.RED + "1. Wildcard Emails")
    print(Fore.CYAN + "2. IP Addresses")
    print(Fore.GREEN + "3. Emails")
    print(Fore.YELLOW + "4. Countries")
    print(Fore.MAGENTA + "5. ASNs")
    print(Fore.BLUE + "6. Exit")
    print(" ")
    print(" ")
    print(" ")
    print(" ")
    print(Fore.GREEN + "https://github.com/zayys-services/sellapp-blacklist")
    print(" ")
    print(" ")
    print(" ")
    print(" ")

    while True:
        selection = input(Fore.YELLOW + "Please select an option: ")
        if selection == '1':
            os.system("CLS")
            blacklist_option = "WILDCARD_EMAIL"
            blacklist_directory = "./data/Wildcard_Emails.txt"
            break
        elif selection == '2':
            os.system("CLS")
            blacklist_option = "IP"
            blacklist_directory = "./data/IPs.txt"
            break
        elif selection == '3':
            os.system("CLS")
            blacklist_option = "EMAIL"
            blacklist_directory = "./data/Emails.txt"
            break
        elif selection == '4':
            os.system("CLS")
            blacklist_option = "COUNTRY"
            blacklist_directory = "./data/Countries.txt"
            break
        elif selection == '5':
            os.system("CLS")
            blacklist_option = "ASN"
            blacklist_directory = "./data/ASNs.txt"
            break
        elif selection == '6':
            os.system("CLS")
            print(Fore.RED + "Exiting...")
            exit()
        else:
            print(Fore.RED + "Invalid selection. Please try again.")

if __name__ == "__main__":
    main()
