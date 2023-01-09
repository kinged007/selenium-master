from src.base import *
from src.webclient import *

from datetime import datetime
import calendar, shutil

def last_day_of_month(year, month):
	# Get the number of days in the month
	num_days = calendar.monthrange(year, month)[1]

	# Create a date object for the last day of the month
	last_day = datetime(year, month, num_days)

	return num_days

make_path("data/transaction_reports/")

"""

	Starting Execution Logic
	Loads url and logs in if required.
	# TODO add option to login via config file. will only work if no captcha is required.
 
"""
def start_execution():
	
	# figure out the dates to use
	currentMonth = datetime.now().month - 1 
	currentYear = datetime.now().year
	prevMonth = 12 if currentMonth<1 else currentMonth
	currentYear = currentYear-1 if prevMonth == 12 else currentYear
	print(os.path.exists(os.path.join('data','transaction_reports',f'{currentYear}-{prevMonth}.csv')))
	return
	if os.path.exists(os.path.join('data','transaction_reports',f'{currentYear}-{prevMonth}.csv')): 
		print("Already have report. Aborting.")
		return
	
	# client.test_ip()
	time.sleep(2)
	   
	URL = "https://business.currenciesdirect.com/businessportal/transactions.htm?search_criteria_name=default_activity_history"
	
 	# load page
	client.load_and_check(URL)

	# load saved cookies
	# if client.load_cookies():
	# 	client.driver.get(URL)
	
	# Accept cookie policy
	try:
		client.driver.find_element(By.CSS_SELECTOR, '#onetrust-accept-btn-handler').click()
	except Exception as e:
		print(f"[red]{e}[/red]")

	# Choose English
	try:
		client.driver.find_element(By.CSS_SELECTOR, '#langselectionDiv > div > div:nth-child(1)').click()
	except Exception as e:
		print(f"[red]{e}[/red]")
	
	# check if need to login
	try:
		time.sleep(1)
		client.driver.find_element(By.CSS_SELECTOR, '#loginEmail').send_keys(config.get('App','email'))
		time.sleep(2)
		client.driver.find_element(By.CSS_SELECTOR, '#loginPassword').send_keys(config.get('App','password', raw=True))
		time.sleep(3)
		client.driver.find_element(By.CSS_SELECTOR, '#emailandPassDiv > div > div.l-grid-row.m-stages--box-double-btns.is-active > button').click()
		log.info("Logging in.")
		time.sleep(3)
		# client.save_cookies()
	except Exception as e:
		log.error(e)

	# prepare dates for report
	lastDay = last_day_of_month(currentYear, prevMonth)
	date_from = f"01/{prevMonth}/{currentYear}"
	date_to = f"{lastDay}/{prevMonth}/{currentYear}"
	client.driver.get(f"https://business.currenciesdirect.com/businessportal/transactions.htm?completeCurrentPage=1&pendingCurrentPage=&fromDate={date_from}&toDate={date_to}&search_criteria_name=filter&curr=&status=CLOSED&collectionAcNo=&collectionAccountCurreny=&moneyStatus=&recipientId=&searchtext=")
	
	time.sleep(3)
	client.driver.find_element(By.CSS_SELECTOR, "#body > main > div.grid-x > div > div > div > div > div > div > a").click()
	client.driver.find_element(By.CSS_SELECTOR, "#body > main > div.grid-x > div > div > div > div > div > div > div > ul > li:nth-child(1) > a").click()
	
	time.sleep(10)
	files = os.listdir(client.downloads_path)
	if len(files) > 0:
		# Set the source and destination paths
		src_path = os.path.join(client.downloads_path,files[0])
		dst_path = os.path.join('data','transaction_reports',f'{currentYear}-{prevMonth}.csv')

		# Copy the file to the destination
		shutil.copy(src_path, dst_path)
		log.info(f"Downloaded report for {currentYear}-{prevMonth}.")
	else:
		log.error("Could not download any files.")
  
	time.sleep(5)
 
	return
  

	log.info("Ready to perform App logic.")
 
	run_app_logic()

"""

	Main App Logic
	Executes once browser is open and login has been performed if neccessary.
 
"""
def run_app_logic():
	pass







if __name__ == "__main__":

	client = WebClient()
	if client.initialize_driver():
		client.set_window_size(1000,700) # defaults to x=1920, y=1080
		while client.open_browser():
			config = load_config()
			start_execution()
		client.cleanup()
	sys.exit(0)

