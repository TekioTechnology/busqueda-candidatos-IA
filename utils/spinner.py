# utils/spinner.py

import threading
import itertools
import sys
import time

done = False

def mostrar_spinner(mensaje="Procesando"):
    global done
    done = False

    def animate():
        for c in itertools.cycle(['|', '/', '-', '\\']):
            if done:
                break
            sys.stdout.write(f'\r{mensaje}... {c}')
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\r✔ Procesamiento completado!\n')

    t = threading.Thread(target=animate)
    t.start()
    return lambda: detener_spinner()

def detener_spinner():
    global done
    done = True
