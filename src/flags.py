FLAGS = {}

FLAGS["is_running"] = None
FLAGS["is_backend_active"] = None
FLAGS["is_backend_syncing"] = None
FLAGS["is_backend_ready"] = None
FLAGS["is_api_server_active"] = None

def is_running():
    return bool(FLAGS["is_running"])

def set_run_start():
    FLAGS["is_running"] = True

def set_run_stop():
    FLAGS["is_running"] = False

def set_backend_start():
    FLAGS["is_backend_active"] = True

def set_backend_stop():
    FLAGS["is_backend_active"] = False

def is_backend_active():
    return bool(FLAGS["is_backend_active"])

def set_backend_sync_start():
    FLAGS["is_backend_syncing"] = True

def set_backend_sync_stop():
    FLAGS["is_backend_syncing"] = False

def is_backend_syncing():
    return bool(FLAGS["is_backend_syncing"])

def set_backend_ready():
    FLAGS["is_backend_ready"] = True

def set_backend_not_ready():
    FLAGS["is_backend_ready"] = False

def is_backend_ready():
    return bool(FLAGS["is_backend_ready"])

def set_api_start():
    FLAGS["is_api_server_active"] = True

def set_api_stop():
    FLAGS["is_api_server_active"] = False

def is_api_active():
    return bool(FLAGS["is_api_server_active"])