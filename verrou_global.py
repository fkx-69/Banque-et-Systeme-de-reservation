import threading

verrou_global_banque = threading.Lock()
verrou_global_reservation = threading.Lock()