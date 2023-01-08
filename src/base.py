from src.utils import * 
from rich.console import Console
Console = Console()

make_path("data")
make_path("logs")

if not any([k in sys.argv for k in ['--verbose','-v']]):
	try:
		log.remove(0)
	except:
		pass
	log.add(sys.stderr, level="INFO", enqueue=True, backtrace=True, diagnose=True)	

log.add(os.path.join("logs","log.log"), format="{time:YYYY-MM-DD at HH:mm:ss} {level} | {name}:{function}:{line} {message}", 
	level="INFO", retention="15 days", enqueue=True, backtrace=True, diagnose=True)	




