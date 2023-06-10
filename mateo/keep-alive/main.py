from KeepAlive import KeepAlive
import signal

k = KeepAlive()

def handler(signum, frame):
    k.stop()

try:
    signal.signal(signal.SIGTERM, handler)
    k.run()
except:
    print("Termino")

