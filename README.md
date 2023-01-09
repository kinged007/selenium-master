## Base package for creating Selenium based automations

### Setup
1. To setup, first unzip the repository into a folder on your hard disk. 
2. Make sure Python and PIP (should be installed automatically with Python) is installed.
3. Rename `config_sample.ini` to `config.ini` and edit the parameters. 
4. Edit `main.py` with your browser actions.
5. Execute the `run.sh` or `run.bat` files for Linux/Mac or Windows respectively.

### Config Parameters
#### `specify_chrome_version`
If you are having an issue using the latest version of Chrome, you can specify a version you know works
#### `hide_browser`
Set to `True` or `False`. True will hide the browser from view and run in the background. 
#### `keep_browser_open` 
Set to `True` or `False`. If True, the browser will remain open and will repeat the execution by `seconds_between_executions`. If False the browser will close. You will have to run the script again to make another execution. If you use a CRON job or a TASK SCHEDULE, then you can turn this to FALSE.
#### `seconds_between_executions`
If browser is kept open, you need to set the amount of seconds to wait between executions. 

