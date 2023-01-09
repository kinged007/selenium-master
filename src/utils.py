""" Helper functions """
try:
	import os, sys, configparser, time, random
	from loguru import logger as log
	import psutil
	from sys import platform
	from rich import print

except:
	raise

	
def clear():
	if platform=='win32':
		return os.system('cls')
	else:
		return os.system('clear')

######################## CONFIG AND GLOBALS #########################

MINUTE_IN_SECONDS = 60
HOUR_IN_SECONDS = MINUTE_IN_SECONDS*60
DAY_IN_SECONDS = HOUR_IN_SECONDS*24
WEEK_IN_SECONDS = DAY_IN_SECONDS*7
MONTH_IN_SECONDS = DAY_IN_SECONDS*30

def load_config(file="config.ini", delimiters=("=")):
	
	from pathlib import Path

	config = None

	if os.path.isfile(file):
		config = configparser.ConfigParser(allow_no_value=True, delimiters=delimiters)
		try:
			config.read(file)
		except:
			exit("ERROR loading configuration file.")

	return config

######################## CHROME + SELENIUM #####################
BINARIES_FOLDER = './selenium'
DRIVER_NAME = 'chromedriver.exe' if platform == 'win32' else 'chromedriver'
DRIVER_PATH = os.path.join(BINARIES_FOLDER, DRIVER_NAME)

def kill_chrome():
	for item in psutil.process_iter():
		if 'chrome' in item.name() and item.name().endswith('.exe'):
			try:
				item.kill()
				log.info(f'Killed Chrome with pid {item.pid}')
			except Exception as e:
				log.info(f'Failed to kill Chrome ({e})')


def prepare_driver():
	
	from undetected_chromedriver.patcher import Patcher
	import shutil

	if not os.path.exists(BINARIES_FOLDER):
		os.makedirs(BINARIES_FOLDER)


	log.info('Preparing ChromeDriver')

	patcher = Patcher()
	patcher.data_path = BINARIES_FOLDER
	release = patcher.fetch_release_number()
	patcher.version_main = release.version[0]
	patcher.version_full = release
	path = patcher.unzip_package(patcher.fetch_package())
	shutil.move(path, DRIVER_PATH)
	patcher.auto(DRIVER_PATH)


def prepare_selenium():
	from distutils.sysconfig import get_python_lib
	# disable urllib retries as they cause big delays when closing script

	site = get_python_lib()
	remote_connection_path = os.path.join(site, 'selenium', 'webdriver', 'remote', 'remote_connection.py')

	if not os.path.exists(remote_connection_path):
		raise Exception('Selenium `remote_connection.py` file not found')

	with open(remote_connection_path, 'r') as f:
		remote_connection_content = f.read()

	if "'retries': False" in remote_connection_content:
		log.debug('Selenium already patched')
		return

	remote_connection_content = remote_connection_content.replace("'timeout': self._timeout",
																"'timeout': self._timeout, 'retries': False")

	with open(remote_connection_path, 'w') as f:
		f.write(remote_connection_content)

	log.info('Selenium patched')

#############################################################################

@log.catch()
def printTitle(title):
	# clear()
	print("\n")
	# print("[yellow]"+"= "*20)
	# print("[red bold]"+str(title))
	Console.rule("[bold red]"+title)
	# print("[yellow]"+"= "*20)
	print("\n")

@log.catch()
def printHeading(title):
	print("\n")
	print("[yellow]"+"= "*20)
	print("[red bold]"+str(title))
	print("[yellow]"+"= "*20)
	print("\n")

@log.catch()
def printTable(data:list,header:list=[],col_width:list=[]):
	""" eg: printTable(header=[' #','Type','username','Users','Name'], col_width=[5,10,35,10,30], data=tbl_df)
			tbl_df.append([
				(gr if _type=='Group' else ye) + str(i), 
				_type, 
				'@'+d.entity.username if d.entity.username else '',
				d.entity.participants_count,
				d.entity.title
			])

		>>> width = 5
		>>> for num in range(5,12): 
		...     for base in 'dXob':
		...         print('{0:{width}{base}}'.format(num, base=base, width=width), end=' ')
		...     print()
		...
			5     5     5   101
			6     6     6   110
			7     7     7   111
			8     8    10  1000
			9     9    11  1001
		10     A    12  1010
		11     B    13  1011
	"""
	# TODO
	pass

@log.catch()
def multi_select_from_list(lst:list,question:str=''):
	q = question if question else "Make your selection"
	print("[red]\n Press 'X' or Ctrl+C to to abort...")
	print("[yellow] Note: use a comma to seperate multiple selections; You can use '-' to select a range (eg. 3-10 selects all from 3 to 10)")
	print("[yellow]       Write 'all' to select all options. If 'all' is selected, the next question will allow you to exclude some options.\n")
	s_select = input(f" [yellow][?] {q}: ").lower().split(',')
	_sel = []

	if 'x' in s_select or 'X' in s_select or (len(s_select) == 1 and s_select[0].strip() == ''): 
		return False
	if 'all' in s_select:
		s_select = input("[yellow] [?] (optional) EXCLUDE options: ").lower().split(',')
		_sel = sorted([*set(y for x in s_select if "-" in x for y in range(int(x.split("-")[0].strip()), int(x.split("-")[1].strip())+1 ) if "-" in x),
			*set(int(x) for x in s_select if "-" not in x and x != '' )])
		selected = [lst[int(a)] for a in range(len(lst)) if int(a) not in _sel]
	else:
		_sel = sorted([*set(y for x in s_select if "-" in x for y in range(int(x.split("-")[0].strip()), int(x.split("-")[1].strip())+1 ) if "-" in x),
			*set(int(x) for x in s_select if "-" not in x )])
		selected = [lst[int(a)] for a in _sel]

	return selected

@log.catch()
def select_from_list(lst:list,question:str=''):
	q = question if question else "Make your selection"
	print("[red]\n Press 'X' or Ctrl+C to to abort...")
	s_select = input(f"[yellow] [?] {q}: ").lower()
	_sel = []

	if 'x' in s_select or 'X' in s_select or (len(s_select) == 1 and s_select[0].strip() == ''): 
		return False
	try:
		selected = lst[int(s_select)]
	except:
		print("[red]Bad selection\n")
		return select_from_list(lst,question)

	return selected


@log.catch()
def make_path(path):
	""" makes directories for given path """
	os.makedirs(path, exist_ok=True)
	return
	try:
		from pathlib import PurePath
		parts = PurePath(path).parts
		pth = ''
		for x in parts:
			if '.' in x or os.path.isfile(os.path.join(pth,x)): break
			pth = os.path.join(pth,x)
			if not os.path.exists(pth): os.mkdir(pth)
		return True
	except Exception as e:
		log.error(e)
	return False


@log.catch()
async def async_wait(t=0):
	import asyncio
	if not t:
		t = random.randrange(10,30)
	if NOWAIT:
		t = 1 
	log.opt(depth=2).debug(f"Waiting for {t} seconds.")
	await asyncio.sleep(t)

@log.catch()
def wait(t):
	if not t:
		t = random.randrange(10,30)
	log.opt(depth=2).debug(f"Waiting for {t} seconds.")
	if NOWAIT:
		t = random.randrange(3,6)
	time.sleep(t)

""" spacer text """
@log.catch()
def sp(length=1):
	o = " "*(int(length))
	return o

""" Clean text from ascii characters and emojis """
@log.catch()
def cleanString(inputString):
	return replace_all(inputString.encode('ascii', 'ignore').decode('ascii'), {
		'"':'',
		"'":'',
		"/":'_',
		"\\" : '_',
		"@" : "_at_",
		
		})

""" replace string with search:value dict """
@log.catch()
def replace_all(text, dic):
	for i, j in dic.items():
		text = text.replace(i, j)
	return text


""" Merge dictionaries """
@log.catch()
def merge_dicts(default: dict, *data: tuple, overwrite=True ):
	if data:
		for d in data:
			for k in d.keys():
				if isinstance(d[k],dict):
					if not k in default:
						default[k] = {}
					default[k] = merge_dicts(default[k],d[k], overwrite=overwrite)
					# for kk in d[k]:
					#   default[k][kk] = d[k][kk]
				else:
					if k in default and default[k] != d[k] and not overwrite: continue
					default[k] = d[k]
	return default  

""" debug helper to print configparser objects """
def print_config(config, return_value=False):
	if return_value: return str({section: dict(config[section]) for section in config.sections()})
	print(str({section: dict(config[section]) for section in config.sections()}))

""" opens a continious stream of the text file and reads all new lines """
def stream_text_file(thefile):
	thefile.seek(0,2)
	while True:
		line = thefile.readline()
		if not line:
			time.sleep(0.1)
			continue
		yield line

""" outputs the time in nice format """
@log.catch()
def FormatTime():
	return time.strftime("%x %X",time.localtime())


""" generates a random password """
@log.catch()
def GeneratePassword(self):
	import string,random
	characters = list(string.ascii_letters + string.digits)
	## shuffling the characters
	random.shuffle(characters)

	## picking random characters from the list
	password = []
	for i in range(9):
		password.append(random.choice(characters))

	## shuffling the resultant password
	random.shuffle(password)

	## converting the list to string
	## printing the list
	return "".join(password)

@log.catch()
def isfloat(num):
	try:
		float(num)
		return True
	except ValueError:
		return False

###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################

# setting cron job
# see https://pypi.org/project/python-crontab/ 
@log.catch()
def create_cron(name='',minutes="0",hours="*",days_of_month="*",days_of_week="*",month="*"):
	basepath = os.path.dirname(os.path.dirname(__file__))
	
	if platform=='win32':
		os.system('cls')	
		print("""
████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
█░░░░░░░░░░█░░░░░░██████████░░░░░░█░░░░░░░░░░░░░░█░░░░░░░░░░░░░░█░░░░░░░░░░░░░░░░███░░░░░░░░░░░░░░█░░░░░░░░░░░░░░█░░░░░░██████████░░░░░░█░░░░░░░░░░░░░░█
█░░▄▀▄▀▄▀░░█░░▄▀░░░░░░░░░░░░░░▄▀░░█░░▄▀▄▀▄▀▄▀▄▀░░█░░▄▀▄▀▄▀▄▀▄▀░░█░░▄▀▄▀▄▀▄▀▄▀▄▀░░███░░▄▀▄▀▄▀▄▀▄▀░░█░░▄▀▄▀▄▀▄▀▄▀░░█░░▄▀░░░░░░░░░░██░░▄▀░░█░░▄▀▄▀▄▀▄▀▄▀░░█
█░░░░▄▀░░░░█░░▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀░░█░░▄▀░░░░░░▄▀░░█░░▄▀░░░░░░▄▀░░█░░▄▀░░░░░░░░▄▀░░███░░░░░░▄▀░░░░░░█░░▄▀░░░░░░▄▀░░█░░▄▀▄▀▄▀▄▀▄▀░░██░░▄▀░░█░░░░░░▄▀░░░░░░█
███░░▄▀░░███░░▄▀░░░░░░▄▀░░░░░░▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀░░████░░▄▀░░███████░░▄▀░░█████░░▄▀░░██░░▄▀░░█░░▄▀░░░░░░▄▀░░██░░▄▀░░█████░░▄▀░░█████
███░░▄▀░░███░░▄▀░░██░░▄▀░░██░░▄▀░░█░░▄▀░░░░░░▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀░░░░░░░░▄▀░░███████░░▄▀░░█████░░▄▀░░░░░░▄▀░░█░░▄▀░░██░░▄▀░░██░░▄▀░░█████░░▄▀░░█████
███░░▄▀░░███░░▄▀░░██░░▄▀░░██░░▄▀░░█░░▄▀▄▀▄▀▄▀▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀▄▀▄▀▄▀▄▀▄▀░░███████░░▄▀░░█████░░▄▀▄▀▄▀▄▀▄▀░░█░░▄▀░░██░░▄▀░░██░░▄▀░░█████░░▄▀░░█████
███░░▄▀░░███░░▄▀░░██░░░░░░██░░▄▀░░█░░▄▀░░░░░░░░░░█░░▄▀░░██░░▄▀░░█░░▄▀░░░░░░▄▀░░░░███████░░▄▀░░█████░░▄▀░░░░░░▄▀░░█░░▄▀░░██░░▄▀░░██░░▄▀░░█████░░▄▀░░█████
███░░▄▀░░███░░▄▀░░██████████░░▄▀░░█░░▄▀░░█████████░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░█████████░░▄▀░░█████░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░░░░░▄▀░░█████░░▄▀░░█████
█░░░░▄▀░░░░█░░▄▀░░██████████░░▄▀░░█░░▄▀░░█████████░░▄▀░░░░░░▄▀░░█░░▄▀░░██░░▄▀░░░░░░█████░░▄▀░░█████░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀▄▀▄▀▄▀▄▀░░█████░░▄▀░░█████
█░░▄▀▄▀▄▀░░█░░▄▀░░██████████░░▄▀░░█░░▄▀░░█████████░░▄▀▄▀▄▀▄▀▄▀░░█░░▄▀░░██░░▄▀▄▀▄▀░░█████░░▄▀░░█████░░▄▀░░██░░▄▀░░█░░▄▀░░██░░░░░░░░░░▄▀░░█████░░▄▀░░█████
█░░░░░░░░░░█░░░░░░██████████░░░░░░█░░░░░░█████████░░░░░░░░░░░░░░█░░░░░░██░░░░░░░░░░█████░░░░░░█████░░░░░░██░░░░░░█░░░░░░██████████░░░░░░█████░░░░░░█████
████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
		""")
		print("Because you are using Windows system, you need to set up the following cron job using Windows Task Scheduler. We can't do it automatically for you. Sorry.")
		print("Instructions:")
		print("1) Open Task Scheduler and Create Task (NOT Basic Task!).")
		if name: print(f"2) Give Name '{name}'.")
		else: print(f"2) Give a useful Name you will use to identify it.")
		print("3) Check 'Run whether user is logged in or not'.")
		print("4) Add New Trigger and set it to Daily, recuring every X day.")
		print("5) Change Advanced Settings: Specify repeat settings. Uncheck 'Expire' and click Ok.")
		print("6) Add New Action: Start a Program.")
		print("7) Program/Script: "+os.path.join(basepath, 'run.bat'))
		# print("8) Additional Arguments (in this order!) : --cron --run")
		print("")		
		input(" [?] Press Enter to continue...")

	else:
		
		from crontab import CronTab
		cron = CronTab(user=True)
		if len(list(cron.find_comment(name))) == 0:
			# job = cron.new(command=" ".join([sys.executable,os.path.join(DIR['BASE'],"Cron.py"),"--run"]))
			# job = cron.new(command=" ".join(['sh',os.path.join(DIR['BASE'],"runx.sh"),"--cron","--run"]))
			job = cron.new(command=" ".join(['sh',os.path.join(basepath,"run.sh"),"--cron","--run",">>",os.path.join(basepath,'logs',"cron_output.log"),"2>&1"]))
			# job.minute.every(5)
			job.setall(f'{minutes} {hours} {days_of_month} {month} {days_of_week}')

			job.set_comment(name)
			cron.write()
			print("Successfully set up Cron Job")
   
   

      
