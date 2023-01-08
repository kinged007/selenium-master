## XT.COM Auto Sell Tokens without using API

### Setup
1. To setup, first unzip the repository into a folder on your hard disk. 
2. Make sure Python and PIP (should be installed automatically with Python) is installed.
3. Rename `config_sample.ini` to `config.ini` and edit the parameters. Set `hide_browser` to `False` on the first run, so you can login to xt.com. The app will save the login cookies so you do not have to loging again. If you login to your xt.com account from another browser, you will need to repeat this process.
4. Execute the `run.sh` or `run.bat` files for Linux/Mac or Windows respectively.

### Config Parameters
#### `specify_chrome_version`
If you are having an issue using the latest version of Chrome, you can specify a version you know works
#### `sell_token_amount`
Set the amount of tokens you want to sell.
#### `hide_browser`
Set to `True` or `False`. True will hide the browser from view and run in the background. You need to see the browser on the first run so you can loging to your xt.com account. After that, the app will restore your login cookies so you do not need to log in again. If you login from another browser, you will need to login again.
#### `keep_browser_open` 
Set to `True` or `False`. If True, the browser will remain open and will repeat the execution by `seconds_between_trades`. If False the browser will close. You will have to run the script again to execute another trade. If you use a CRON job or a TASK SCHEDULE, then you can turn this to FALSE.
#### `seconds_between_trades`
If browser is kept open, you need to set the amount of seconds to wait between trade executions. Recommended to be at least 300-600 seconds (5-10 minutes), depending on the amount of tokens being sold.
#### `market_or_limit`
Set to `market` or `limit`. Market will execute trade at Market price. Limit will execute trade at defined limit price (set by `limit_price` below)
#### `limit_price`
Set the price to create Limit orders, if `market_or_limit` is set to limit. If this is left empty, the market price when the page is loaded will be used instead.

### Remember
You need to see the browser on the first run so you can loging to your xt.com account. After that, the app will restore your login cookies so you do not need to log in again. If you login from another browser, you will need to login again.