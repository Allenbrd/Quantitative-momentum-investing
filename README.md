# Quantitative Momentum Investing
This program picks the most valuable stocks to invest in based on their 1 year return performance.
The stocks are selected amongst USA's 500 largest public companies.
The user enters his portfolio's value, and an order sheet is generated. This order sheet contains all shares and quantities to buy at the current market value.

## How to use this code
1. Register/Login to https://iexcloud.io/ and get your secret API token from your profile.

2. Create a file named mysecrets.py in the repository's root.

3. In mysecrets.py, add a string variable named 'IEX_CLOUD_API_TOKEN' that is equal to your IEX Cloud API token.

4. Run ```'pip install -r requirements.txt'```

And you are all set!
