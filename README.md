# Domain Blacklister

Domain Blacklister is a Python script designed to manage and update domain blacklists using Sell.app API. It supports multi-threaded processing with proxy rotation for efficient operation.

## Features

- **API Integration:** Interacts with Sell.app API to fetch existing blacklisted domains and add new ones.
- **Multi-threaded Processing:** Utilizes threading for concurrent domain processing, improving speed.
- **Proxy Support:** Rotates through a list of proxies to handle rate limits and network errors gracefully.
- **File Handling:** Reads domains and proxies from text files for easy configuration.

## Setup

### Prerequisites

- Python 3.x installed on your system.
- `pip` package manager to install Python dependencies.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/MrPrinceV2/sell.app-Blacklist-Rules.git
   cd domain-blacklister
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up Sell.app API key:
   - Go to `api/sell.app.apikey` and open it in notepad.
   - Make sure your Sell.app API key has blacklist permissions.
   - Paste your Sell.app API key into this file.

4. Prepare domain and proxy files:
   - Add or remove any domains or proxies in `data/domains.txt` and `data/proxies.txt` files.

### Usage

Run the script using Python:

```bash
python main.py
```

Or you can run the `start.bat` file.

### Notes

- Ensure `domains.txt` and `proxies.txt` are correctly formatted before running the script.
- Monitor console output for status updates and errors during execution.

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests with improvements or bug fixes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
