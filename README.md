# Trabajo Práctico 1 - Sistemas Distribuidos
> Alumno: Gonzalo Sabatino. Padrón: 104609.

- [Link al set de datos](https://www.kaggle.com/datasets/jeanmidev/public-bike-sharing-in-north-america).
- [Link a notebook de muestra de comandos](https://www.kaggle.com/code/pablodroca/bike-rides-analyzer).

## Video de ejecución del sistema
[Enlace al video](https://youtu.be/6_RNVpIEv2g).

## Ejecución
> Nota: La estructura de los archivos de datos debe ser data/montreal, data/toronto, data/washington. Tal cual como fue bajada de kaggle.


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
make server-run
```

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
make client-run
```

* Para dar de baja al cliente
```bash
make client-down
```

## Modificación de parámetros
En el archivo `config.json`, una de las entradas es `amount_nodes`, que especifica cuántos de cada componente se van a desplegar. Un ejemplo:
```json
"amount_nodes": {
	"filter_year": 2,
	"filter_pretoc": 1,
	"filter_distance": 1,
	"applier_query1": 1,
	"applier_query2": 2,
	"applier_query3": 1
}
```

Si se quiere modificarlo, luego se debe ejecutar el programa de python
```python
python3 create_docker_compose.py
```

que modifica el `docker-compose` del servidor según los parámetros deseados.