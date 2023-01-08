from src.base import *
from src.webclient import *


"""

	Starting Execution Logic
	Loads url and logs in if required.
	# TODO add option to login via config file. will only work if no captcha is required.
 
"""
def start_execution():
    
	# client.test_ip()
 
	

	URL = "https://www.xt.com/tradePro/snack_usdt"

	if not client.load_and_check(URL, title="XT.COM"):
		client.cleanup()
		sys.exit(0)

	log.info(f"Successfully loaded '{URL}'")

	time.sleep(7)

	button = client.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div[2]/div[2]/div[2]/div[2]/button/span')
	if 'login' in button.text.lower():
		# load cookies
		if client.load_cookies():
			client.driver.get(URL)
		else:
			log.info("Requires Manual Login...")
			client.driver.get('https://accounts.xt.com/en-US/login?backurl=https%3A%2F%2Fwww.xt.com%2FtradePro%2Fsnack_usdt')

	# token has expired. Restart
	try:
		token_expire = client.driver.find_element(By.XPATH, '/html/body/div[4]/div/div[2]/div[1]')
		if token_expire and 'expire' in token_expire.text.lower():
			log.debug("Expired token!")
			return start_execution()
	except:
		pass
	
	
	# Waiting for user to login
	while True:
		try:
			button = client.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div[2]/div[2]/div[2]/div[2]/button/span/span')
			if "sell" in button.text.lower(): # check element for logged in users
				# logged in. save cookies
				client.save_cookies()
				break
		except:
			log.debug("Waiting for user to login")
			time.sleep(5)
			continue

	log.info("Ready to perform App logic.")
 
	run_app_logic()

"""

	Main App Logic
	Executes once browser is open and login has been performed if neccessary.
 
"""
def run_app_logic():
    
	snack_balance_elem = client.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div[2]/div[2]/div[2]/div[2]/div[1]/div[1]/span/b')
	usdt_balance_elem = client.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div[2]/div[2]/div[2]/div[1]/div[1]/div/span/b')
	exch_price = client.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div/div[1]/div[2]/div[1]/div[3]/div[2]/div/span/b').text
	buy_price = client.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div/div[1]/div[2]/div[1]/div[3]/div[3]/div[1]/div[2]/div[1]/span').text
	log.debug(buy_price)

	snack_balance = float(snack_balance_elem.text.replace(",",""))
	usdt_balance = float(usdt_balance_elem.text.replace(",",""))
	log.info(f"Current Balance: {snack_balance} SNACK" )
	log.info(f"Current Balance: {usdt_balance} USDT" )
	log.info(f"Current Price: 1 SNACK = {exch_price} USDT" )

	sell_amount = float(config.get('App','sell_token_amount',fallback='0'))

	if snack_balance > sell_amount:
		log.info("Sufficient balance to sell")

		time.sleep(17)

		exch_price = client.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div/div[1]/div[2]/div[1]/div[3]/div[2]/div/span/b').text.replace(',','')

		if 'market' in config.get('App','market_or_limit',fallback='market').lower():
			client.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div[2]/div[2]/div[1]/div/button[2]').click()
			sale_price = exch_price
		else:
			client.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div[2]/div[2]/div[1]/div/button[1]').click()
			lp = config.get('App','limit_price',fallback=0)
			sale_price = float(lp) if isfloat(lp) and float(lp) > 0 else buy_price
			try:
				limit_elem = client.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div[2]/div[2]/div[2]/div[2]/div[2]/div[1]/input')
				limit_elem.clear()
				limit_elem.send_keys(str(sale_price))
			except Exception as e:
				log.error(e)

		log.info(f"Selling {sell_amount} SNACK tokens at {sale_price} for {sell_amount*float(sale_price):.6f} USDT")

		sell_element = client.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div[2]/div[2]/div[2]/div[2]/div[2]/div[2]/input')

		sell_element.clear()
		sell_element.send_keys(str(sell_amount))

		client.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div[2]/div[2]/div[2]/div[2]/button').click()

	else:
		log.warning("Insufficient token balance. ")

	time.sleep(10)








if __name__ == "__main__":

	client = WebClient()
	if client.initialize_driver():
		client.set_window_size() # defaults to x=1920, y=1080
		while client.open_browser():
			config = load_config()
			start_execution()
		client.cleanup()
	sys.exit(0)

