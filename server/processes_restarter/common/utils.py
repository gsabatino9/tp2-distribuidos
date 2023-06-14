

ARE_YOU_ALIVE_MESSAGE = b'L'

# Si un contenedor no responde luego de HEALTHCHECK_TIMEOUT, se lo considera parado.
HEALTHCHECK_TIMEOUT = 0.5
# tiempo minimo para el timeout del healthcheck (asi no se setea en negativo o en 0)
MINIMUM_TIMEOUT_TIME = 0.1
TIME_BETWEEN_HEALTHCHECKS = 1.0

# Luego de hacer un restart, siempre tarda al menos un poquito en levantar el contenedor.
# Por eso se duerme un poco antes de intentar crear la primera conexion.
INIT_TIME_SLEEP = 1.0

# Este tiempo es el maximo que deberia tardar un container en levantar desde que se
# le hace restart. Si no se puede hacer una conexion en este tiempo, se hace un restart.
MAX_TIME_SLEEP = 5.0
