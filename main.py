import sys
import time
import threading
from src.api.api_main import start_api_server
from src.backend.backend_main import start_backend_process
import config as config

DELAY_API_SERVER_START = 60 # 1 min

def convert_to_dict(module):
    context = {}
    for setting in dir(module):
        if not setting.startswith("__"):
            context[setting] = getattr(module, setting)
    return context

if __name__ == "__main__":
    
    # parse the config file into dict
    _config = convert_to_dict(config)
    
    # start the backend process (token scanner). pass reset=True if --reset is in command-line args
    if "--reset" in sys.argv or "-r" in sys.argv:
        t1 = threading.Thread(target=lambda:start_backend_process(config=_config, reset=True))
    else:
        t1 = threading.Thread(target=lambda:start_backend_process(config=_config))
    t1.start()
    # sleep until backend is started, so that API server can function correctly (TODO: sleep until backend process returns some flag indicating its started)
    time.sleep(DELAY_API_SERVER_START)
    
    # start the API server
    t2 = threading.Thread(target=lambda: start_api_server(config=_config))
    t2.start()

    t1.join()
    t2.join()
