from src.base import * 

from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# import seleniumwire.webdriver as driver
# import undetected_chromedriver as driver
import seleniumwire.undetected_chromedriver as driver
from selenium_stealth import stealth
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import httpx, asyncio, tempfile, pickle
# from httpx_socks import AsyncProxyTransport
from fake_useragent import UserAgent


class WebClient():

	

	@log.catch()
	def __init__(self, **kwargs):

		self.config = load_config()

		self.start_timer = time.time()

		self.headless = self.config.getboolean('Common','hide_browser',fallback=False)
		self.headless = True if '--headless' in sys.argv else self.headless
		self.undetected_driver = False
		self.proxy = self.get_proxy() if self.config.getboolean("Common","use_proxies",fallback=False) else None
		self.version = self.config.get('Common','specify_chrome_version',fallback='0')
		self.version = int(self.version) if isfloat(self.version) else 0

		# self.http_client = httpx.AsyncClient(transport=AsyncProxyTransport.from_url(self.proxy))

		self.cleaned_up = False

		self.downloads_path = os.path.normpath(tempfile.TemporaryDirectory().name)
		self.user_data = os.path.normpath(tempfile.TemporaryDirectory().name)

		if kwargs:
			for k in kwargs.keys():
				self.__dict__[k] = kwargs[k]

		os.makedirs(self.downloads_path, exist_ok=True)
		os.makedirs(self.user_data, exist_ok=True)
  
		self.first_run = True

		# asyncio.run(self.start())


	@log.catch()
	def __del__(self):
		log.debug("Closing...")
		try:
			self.cleanup()
			self.driver.quit()
		except:
			log.error("Problem occured when cleaning up: " + str(e) )

		log.debug("Elapsed time to complete task: " + str(time.time() - self.start_timer) + " seconds")
		pass

	@log.catch()
	def cleanup(self):
		log.info("Closing browser and cleaning up.")
		try:
			loop = asyncio.get_event_loop()
			if loop.is_running():
				loop.create_task(self.http_client.aclose())
			else:
				loop.run_until_complete(self.http_client.aclose())
		except:
			pass

		if self.cleaned_up:
			return

		self.cleaned_up = True

		if hasattr(self, 'driver') and self.driver:
			try:
				self.driver.close()
				self.driver.quit()
			except:
				log.warning('Failed to close the driver normally')

			for driver_process in self.driver_processes:
				try:
					driver_process.kill()
				except:
					pass    
		
		log.debug("Finished cleaning up.")

	@log.catch()
	def get_proxy(self):
		proxy = None
		proxy_path = os.path.join('data','proxies.txt')
		if not os.path.isfile(proxy_path):
			log.warning("No proxies file found. Please create a text file in 'data/proxies.txt'")
			return None
		
		from random import choice
		
		with open(proxy_path, 'r', encoding='utf-8') as f:
			lines = f.readlines()
			if len(lines) == 0: 
				log.warning("Proxy file is empty")
				return None
			proxy = choice(lines).replace('\n','').strip()

		if proxy and "@" not in proxy:
			_p = proxy.split(":")
			if len(_p) == 4:
				proxy = f"{_p[2]}:{_p[3]}@{_p[0]}:{_p[1]}"
			
		# PROXIES = { 
		# 	'http' : f'socks5://{proxy}',
		# 	'https' : f'socks5://{proxy}'
		# 	}     
		# HEADERS = ({'User-Agent': self.random_useragent(),
		# 			'Accept-Language': 'en-US, en;q=0.5',
		# 			'Accept-Encoding': 'gzip, deflate',
		# 			'Accept' : 'test/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		# 			'Referer': 'https://www.google.com/'
		# 			})

		if proxy:
			log.info("Using proxy: " + str(proxy))
   
		return proxy

	@log.catch()
	def random_useragent(self):
		ua = UserAgent()
		userAgent = ua.random
		return userAgent
	
	@log.catch()
	def initialize_driver(self):

		prepare_selenium()

		# kill_chrome()

		prepare_driver()
		
		try:
			options = driver.ChromeOptions()
			options.add_argument(
				'--no-first-run --no-service-autorun --no-default-browser-check --no-sandbox --password-store=basic')
			options.add_argument('--disable-dev-shm-usage')
			options.add_argument('--disable-extensions')
			options.add_argument('--disable-infobars')
			options.add_argument('--disable-notifications')
			options.add_argument('--disable-component-cloud-policy')
			options.add_argument('--disable-sync')

			options.add_argument('--allow-file-access-from-files')
			# options.add_argument('--disable-web-security')

			# options.add_argument('--user-data-dir=' + self.user_data)
			options.add_argument('--profile-directory=Profile 1')
			options.add_argument('--allow-profiles-outside-user-dir')
			options.add_argument('--enable-profile-shortcut-manager')
			options.add_argument('--profiling-flush=3')
			options.add_argument('--enable-aggressive-domstorage-flushing')
   
			# Add the user agent to the ChromeOptions instance
			ua = self.random_useragent()
			# if ua:
			# 	options.add_argument(f"user-agent={ua}")

			# if not self.headless:
			# 	options.add_argument('--disable-blink-features=AutomationControlled')
			# 	options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
			# 	options.add_experimental_option('useAutomationExtension', False)

			options.add_experimental_option('prefs', {
				'download.default_directory': self.downloads_path,
				'savefile.default_directory': self.downloads_path,
				'download.prompt_for_download': False,
				'download.directory_upgrade': True,
				'safebrowsing.enabled': True,
				'download.safebrowsing.enabled': True
			})

			seleniumwire_options = {
				'verify_ssl': False,
				'ignore_http_methods': ['OPTIONS', 'PUT', 'DELETE'],
				'backend': 'mitmproxy'
			}
			if self.proxy:
				seleniumwire_options['proxy'] = {
						'http': f'socks5://{self.proxy}',
						'https': f'socks5://{self.proxy}',
					}
			
			# log.error("TODO Fix proxy setting") # seems to be working now

			if self.headless:
				options.add_argument('--headless')
   
			driver_options = {
				'options': options, 
				'seleniumwire_options': seleniumwire_options,
				'executable_path': DRIVER_PATH
			}


			if self.version != 0: driver_options['version_main'] = int(self.version)

			self.driver: Optional[driver.Chrome] = driver.Chrome(**driver_options,
																 desired_capabilities=options.to_capabilities())

			self.driver_processes = psutil.Process(self.driver.service.process.pid).children(recursive=True)

			self.driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
			params = {'cmd': 'Page.setDownloadBehavior',
					  'params': {'behavior': 'allow', 'downloadPath': self.downloads_path}}

			self.driver.execute("send_command", params)

			# stealth mode. seems to be required for headless and anti-bot detection
			stealth(self.driver, platform='Win32',  # noqa
					user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36 Edg/103.0.1264.37')
		except Exception as e:
			log.error(e)
			return False

		return self.driver
		# return True

	@log.catch()
	def set_window_size(self, x=1920, y=1080):

		if not self.headless:
			self.driver.set_window_size(x, y)
			self.driver.set_window_position(0, 0)
	 
 
	@log.catch()
	def has_cookies(self):
		if os.path.isfile(os.path.join("data","cookies.pkl")): return True
		return False

	@log.catch()
	def load_cookies(self):

		if self.has_cookies():
			try:
				cookies = pickle.load(open(os.path.join("data","cookies.pkl"),"rb"))
				for cookie in cookies:
					self.driver.add_cookie(cookie)
				log.info("Successfully loaded Cookies.")
				return True
			except:
				os.remove(os.path.join("data","cookies.pkl"))
    
		return False
			  
	@log.catch()
	def save_cookies(self):
		pickle.dump( self.driver.get_cookies() , open(os.path.join("data","cookies.pkl"),"wb"))
		log.info("Saved Cookies.")
		
	@log.catch()
	def load_and_check(self, URL, title=""):     
		try:
			self.driver.get(URL)
			self.driver.implicitly_wait(30)  # wait a bit
			time.sleep(3)
			if not title: return True
   
			# Define a custom condition
			def element_has_text(driver):
				# element = driver.find_element(By.TAG_NAME, "title")
				element = driver.title
				return title in element

			log.debug("Waiting for title to contain the following text: "+title)

			# Wait for the custom condition to be met
			WebDriverWait(self.driver, 120).until(element_has_text)
   
			if title and not title in self.driver.title:
				log.error("Wrong Page title:" + str(self.driver.title) )
				return False
			# should have the right page
			return True

		except Exception as e:
			log.error(e)
			return False

	@log.catch()
	def what_is_my_ip(self):
		self.driver.get("https://api.ipify.org")
		# print(self.driver.page_source)
		return self.driver.page_source
	 
	@log.catch()
	def open_browser(self, value=True):
		keep_browser_open = self.config.getboolean('Common','keep_browser_open',fallback=False)
     
		if self.first_run:
			if keep_browser_open: log.info("Keeping browser open")
			else: log.info("Running a single execution")
			self.first_run = False
			return True

		if keep_browser_open:
			seconds_between_executions = self.config.getint('Common','seconds_between_executions',fallback=300)
			print(f"Sleeping for {seconds_between_executions} seconds...")
			time.sleep(seconds_between_executions)			
			return True
		else:
			time.sleep(5)
		
		return False
	 
	 
	 
	 
	@log.catch()
	async def start(self):

	
		self.initialize_driver()

		URL = "https://xt.com/"

		self.driver.get(URL)
		time.sleep(10)

		return
		
		# # # use authenticated proxy
		# while True:
		# 	if 'username' not in self.Config['proxy']:
		# 		self.GetProxy()
		# 		continue
		# 	else:
		# 		break

		# # chromedrive path
		# if platform == 'win32':
		#     executable_path = {'executable_path': self.Path(DIR['BASE'],"drivers","chromedriver.exe")}
		# else:
		#     executable_path = {'executable_path': self.Path(DIR['BASE'],"drivers","chromedriver")}

		# # other chrome options
		# chrome_options = webdriver.ChromeOptions()
		# # if not '--no-headless' in sys.argv:
		# # 	chrome_options.add_argument('--headless')
		# chrome_options.add_argument('--no-sandbox')
		# chrome_options.add_argument('--incognito')
		# chrome_options.add_argument('--ignore-certificate-errors-spki-list')
		# chrome_options.add_argument('--ignore-ssl-errors')
		# chrome_options.add_argument('--ignore-certificate-errors')
		# # chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
		# chrome_options.add_experimental_option("detach", True)
		# capabilities = DesiredCapabilities.CHROME.copy()
		# capabilities['acceptInsecureCerts'] = True


		###########

		if self.undetected_driver:
			import seleniumwire.undetected_chromedriver.v2 as driver
		else:
			import seleniumwire.webdriver as driver

		options = driver.ChromeOptions()
		options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
		options.add_argument('--disable-extensions')
		options.add_argument('--disable-infobars')
		options.add_argument('--disable-notifications')
		options.add_argument('--disable-sync')
		options.add_argument('--incognito')
		# options.add_experimental_option("detach", True)

		seleniumwire_options = {
			'verify_ssl': False,
			'ignore_http_methods': ['GET', 'POST', 'OPTIONS'],
			'backend': 'mitmproxy'
		}

		_proxy = self.get_proxy_options()
		if _proxy:
			seleniumwire_options['proxy'] = _proxy

		driver_options = {
			'options': options,
			'seleniumwire_options': seleniumwire_options
		}


		if self.headless:
			options.add_argument('--headless')

		if self.undetected_driver:
			driver_options['driver_executable_path'] = DRIVER_PATH
			driver_options['headless'] = self.headless
		else:
			driver_options['executable_path'] = DRIVER_PATH
			if self.headless:
				options.add_argument('--headless')

			options.add_experimental_option("excludeSwitches", ["enable-logging"])



		self.driver = driver.Chrome(**driver_options)
		self.driver_processes = psutil.Process(self.driver.service.process.pid).children(recursive=True)

		if not self.headless:
			self.driver.set_window_size(1920, 1080)
			self.driver.set_window_position(0, 0)

		###########

		# self.driver = webdriver.Chrome(executable_path['executable_path'], options=chrome_options,
		#                            seleniumwire_options=self.get_proxy_options(), desired_capabilities=capabilities)
		# self.driver = Browser(executable_path['executable_path'], options=chrome_options,seleniumwire_options=self.get_proxy_options(), desired_capabilities=capabilities)

		AcceptedResponseCodes = [200,
								 302]  # 302 should be accepted if we are not loading images (resources are redirected away)

		# URL = "https://www.whatismyip.com/"
		# URL = "http://my.telegram.org/"
		URL = "https://xt.com/"

		_failed_attempts = 5

		while True:
			if _failed_attempts <= 0:
				log.error("Could not connect multiple times.")
				self.driver.quit()
				# await self.client.Disconnect()
				return
			# try to connect
			try:
				self.driver.get(URL)
				self.driver.implicitly_wait(5)  # wait a bit
				# time.sleep(10)
				if not self.driver.title == 'Telegram Web':
					print(self.driver.title)
					time.sleep(3)
					continue
				# should have the right page
				break

			except Exception as e:
				log.error(e)

				_failed_attempts -= 1
				continue

		print(f"Successfully loaded '{URL}'")



	# async def click():


	# 	self.client = TelethonClient(self.SessionName)

	# 	if not await self.client.ConnectClient():
	# 		log.error("Could not connect to client.")
	# 		return

	# 	while True:
	# 		try:
	# 			# await async_wait(2)
	# 			ph = self.driver.find_element(By.XPATH, '//*[@id="auth-pages"]/div/div[2]/div[1]/div/div[3]/div[2]/div[1]')
	# 			break
	# 		except:
	# 			try:
	# 				self.driver.find_element(By.XPATH, '//*[@id="auth-pages"]/div/div[2]/div[2]/div/div[2]/button').click()
	# 				continue
	# 			except Exception as e:
	# 				log.error(e)
	# 				self.driver.quit()
	# 				await self.client.Disconnect()
	# 				return

	# 	# assuming got a good response. continue

	# 	try:
	# 		await async_wait(2)
	# 		ph.clear()
	# 		await async_wait(1)
	# 		ph.send_keys('+' + str(self.metadata.get('phone')))
	# 		button = self.driver.find_element(By.XPATH, '//*[@id="auth-pages"]/div/div[2]/div[1]/div/div[3]/button[1]')
	# 		button.click()

	# 	except Exception as e:
	# 		log.error(e)
	# 		self.driver.quit()
	# 		await self.client.Disconnect()
	# 		return

	# 	print("Waiting for Login code.")
	# 	# print("looking for"+str(self.Session['me'].phone)[-4:] )
	# 	# # Wait until password box appears
	# 	# print("in "+self.driver.find_element(By.CLASS_NAME, 'phone').text)
	# 	# WebDriverWait(self.driver, timeout=10).until(lambda d: str(self.Session['me'].phone)[-4:] in d.find_element(By.CLASS_NAME, 'phone').text  )
	# 	self.driver.implicitly_wait(10)  # wait a bit

	# 	# enter password
	# 	code = ''
	# 	while not code:
	# 		# getting code
	# 		print("Getting confirmation code...")
	# 		await async_wait(3)
	# 		code = await self.client.GetConfirmationCode()
	# 		pass

	# 	log.info("Telegram Web Login Authentication code received: " + code)

	# 	try:
	# 		self.driver.implicitly_wait(10)  # wait a bit

	# 		self.driver.find_element(By.XPATH, '//*[@id="auth-pages"]/div/div[2]/div[3]/div/div[3]/div/input').send_keys(
	# 			code)

	# 	except Exception as e:
	# 		log.error(e)
	# 		await self.client.Disconnect()
	# 		self.driver.quit()

	# 	await async_wait(5)

	# 	try:
	# 		c = self.driver.find_element(By.XPATH, '//*[@id="auth-pages"]/div/div[2]/div[4]').get_attribute("class")
	# 		if 'active' in c or self.metadata.get('twoFA') != "" :
	# 			# expecting password
	# 			print("2FA is Enabled...")
	# 			# try:
	# 			# 	from easygui import msgbox
	# 			# 	msgbox("If it doesn't work automatically, you can use this password:\n"+self.metadata.get('twoFA'), title="2FA Password is required")
	# 			# except Exception as e:
	# 			# 	log.error(e)

	# 			self.driver.find_element(By.XPATH,
	# 								 '//*[@id="auth-pages"]/div/div[2]/div[4]/div/div[2]/div/input[2]').send_keys(
	# 				str(self.metadata.get('twoFA')))
	# 			self.driver.find_element(By.XPATH, '//*[@id="auth-pages"]/div/div[2]/div[4]/div/div[2]/button').click()
	# 	except:
	# 		pass

	# 	# WebDriverWait(self.driver, timeout=10).until(lambda d: d.find_element(By.ID, 'page-chats')  )

	# 	print("logged in!")

	# 	# try:
	# 	# 	self.driver.find_element(By.ID, 'page-chats')
	# 	# except:
	# 	# 	log.error("Could not find page chats.")
	# 	# 	await self.Client.Disconnect()
	# 	# 	self.driver.quit()
	# 	# 	return

	# 	await self.client.Disconnect()

	# 	while True:
	# 		try:
	# 			await async_wait(30)
	# 			self.driver.title
	# 		except:
	# 			# closed
	# 			self.driver.quit()
	# 			break

	# 	return

	# 	# self.driver.implicitly_wait(100)

	# 	# print(f"Page title: {self.driver.title}")

	# 	# try:
	# 	# 	login_form = self.driver.find_element(By.ID, "my_send_form")
	# 	# except:
	# 	# 	# form cannot be found
	# 	# 	print("Cant find login form.")
	# 	# 	self.driver.quit()
	# 	# 	# self.Client.disconnect()
	# 	# 	return

	# 	# # logout if logged in
	# 	# try:
	# 	# 	self.driver.find_element(By.LINK_TEXT, 'Log out').click()
	# 	# 	print("Browser had a session. Logging out.")
	# 	# 	time.sleep(3)
	# 	# 	self.driver.get('https://my.telegram.org/auth')
	# 	# except:
	# 	# 	pass

	# 	# # login
	# 	# try:
	# 	# 	login_form.find_element(By.ID,'my_login_phone').send_keys('+'+str(self.Session['me'].phone))
	# 	# 	login_form.find_element(By.XPATH, '//*[@id="my_send_form"]/div[2]/button').click()
	# 	# 	print("Waiting for Login code.")
	# 	# except:
	# 	# 	print("Could not find Phone input field.")

	# 	# # Wait until password box appears
	# 	# WebDriverWait(self.driver, timeout=10).until(lambda d: d.find_element(By.ID, 'my_password') )

	# 	# # enter password
	# 	# code = ''
	# 	# while not code:
	# 	# 	# getting code
	# 	# 	code = self.loop.run_until_complete(self.GetConfirmationCode())
	# 	# 	pass

	# 	# log.info("Telegram Web Login Authentication code received: "+code)

	# 	# # free up database
	# 	# self.Client.disconnect()

	# 	# try:
	# 	# 	time.sleep(5)
	# 	# 	self.driver.implicitly_wait(100) # wait a bit
	# 	# 	self.driver.find_element(By.ID, 'my_password').send_keys(code)
	# 	# 	time.sleep(1)
	# 	# 	self.driver.find_element(By.XPATH, '//*[@id="my_login_form"]/div[4]/button').click() # click sign in
	# 	# except:
	# 	# 	log.error("Could not locate password and sign in elements.")
	# 	# 	self.driver.quit()
	# 	# 	# self.Client.disconnect()
	# 	# 	return

	# 	# self.driver.implicitly_wait(10) # wait a bit
	# 	# time.sleep(4)
	# 	# self.driver.get('https://my.telegram.org/apps')

	# 	# try:
	# 	# 	self.driver.find_element(By.ID, 'app_create_form')
	# 	# 	# no app exists
	# 	# 	title = "mytgdapp"+str(random.randrange(100,999))
	# 	# 	self.driver.find_element(By.ID, 'app_title').send_keys(title)
	# 	# 	self.driver.find_element(By.ID, 'app_shortname').send_keys(title.replace(" ","").lower())
	# 	# 	self.driver.find_element(By.XPATH, '//*[@id="app_create_form"]/div[4]/div/div[5]/label').click()
	# 	# 	time.sleep(1)
	# 	# 	self.driver.find_element(By.ID, 'app_save_btn').click()

	# 	# except Exception as e:
	# 	# 	log.error(e)
	# 	# 	# app already exists
	# 	# 	pass

	# 	# time.sleep(100)

	# 	# api_id = api_hash = ''

	# 	# try:
	# 	# 	# account must already have an app configured
	# 	# 	api_id = self.driver.find_element(By.XPATH, '//*[@id="app_edit_form"]/div[1]/div[1]/span/strong').text
	# 	# 	api_hash =  self.driver.find_element(By.XPATH, '//*[@id="app_edit_form"]/div[2]/div[1]/span').text
	# 	# except Exception as e:
	# 	# 	log.error(e)

	# 	# if api_id and api_hash:
	# 	# 	log.info(f"Telegram API Credentials: ID={api_id} | Hash={api_hash}")
	# 	# 	# update database
	# 	# 	self.loop.run_until_complete(self.UpdateSessionToDb(api_id=api_id, api_hash=api_hash))
	# 	# else:
	# 	# 	log.error("Could not find API credentials. Check website has not changed and update code.")

	# 	# # print(self.driver.html)
	# 	# time.sleep(100)
	# 	# self.driver.quit()

	# 	# log.debug("Elapsed time to complete task: "+str(time.time()-_start)+" seconds")
	# 	# # self.Client.disconnect()
	# 	# return

	# 	return
