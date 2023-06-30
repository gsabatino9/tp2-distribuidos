# Trabajo Práctico 2 - Sistemas Distribuidos
Alumnos: 

* Gonzalo Sabatino. Padrón: 104609.
* Mateo Capón Blanquer. Padrón: 104258.
* Luciano Sportelli Castro. Padrón 99565.

- [Link al set de datos](https://www.kaggle.com/datasets/jeanmidev/public-bike-sharing-in-north-america).
- [Link a notebook de muestra de comandos](https://www.kaggle.com/code/pablodroca/bike-rides-analyzer).

## Ejecución
> Nota: La estructura de los archivos de datos debe ser data/client_1, data/client_2, data/client_3, etc. segun la cantidad de clientes. Dentro de estas carpetas deben estar los tres archivos stations.csv, trips.csv y weather.csv, tal cual como fue bajada de kaggle.


**Servidor:**
* Build de imagenes:
```bash
make server-image
```

* Para ejecutar el servidor
```bash
make server-up
```

* Para ejecutar ver los logs del servidor
```bash
make server-logs
```

* Build, ejecución y logs todos juntos
```bash
make server-run random_fails=1
```

Poniendo `random_fails=1` se simulará la caída del sistema. En caso contrario no se caerá nada.

* Para dar de baja al servidor
```bash
make server-down
```

**Cliente:**
* Build de imagenes:
```bash
make client-image
```

* Para ejecutar el cliente
```bash
make client-up
```

* Para ejecutar ver los logs del cliente
```bash
make client-logs
```

* Build, ejecución y logs todos juntos
```bash
make client-run amount_clients=$(cantidad_clientes)
```

* Para dar de baja al cliente
```bash
make client-down
```

## Modificación de parámetros
En el archivo `config.json`, una de las entradas es `amount_nodes`, que especifica cuántos de cada componente se van a desplegar. Un ejemplo:
```json
"amount_nodes": {
	"accepter": 2,
	"filter_year": 2,
	"filter_pretoc": 1,
	"filter_distance": 1,
	"applier_query1": 1,
	"applier_query2": 2,
	"applier_query3": 1
}
```

Dado que la elección de líder usa sockets UDP, se agrega una variable en el archivo `config.json`, `network_problems`, que al ser seteada en 1, simulará la caída de paquetes UDP. 

Si se quiere modificarlo, luego se debe ejecutar el programa de python
```python
python3 create_docker_compose.py
```

que modifica el `docker-compose` del servidor según los parámetros deseados.
