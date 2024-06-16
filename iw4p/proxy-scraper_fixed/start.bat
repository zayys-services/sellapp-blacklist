pip install -r requirements.txt
pause
cls
python proxyScraper.py -p http
pause
cls
python proxyChecker.py -p http -t 20 -s https://google.com -l output.txt
pause
cls