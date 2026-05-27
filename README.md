# Sistema de Gestión de Pedidos — Roles CUGDL

**Materia:** Programación 3  
**Proyecto:** Programación Concurrente  

---

## Nombre del proyecto

**Roles CUGDL — Sistema de gestión de pedidos concurrente**

---

## ¿Qué hace el programa?

El programa simula el flujo completo de un sistema de pedidos para un vendedor de roles dentro del Centro Universitario de Guadalajara. El vendedor ofrece tres tipos de roles: de canela, de pizza y de frutos rojos.

El vendedor recibe pedidos por WhatsApp de forma constante mientras atiende en persona, lo que puede volverse complicado de manejar manualmente. Este sistema simula cómo se podrían procesar esos pedidos de forma automática y eficiente usando programación concurrente.

En concreto, el programa:

- Genera pedidos de forma aleatoria (simulando mensajes de WhatsApp)
- Los acumula en una cola compartida
- Los procesa en paralelo usando varios hilos
- Simula la preparación y entrega de cada pedido a su ubicación
- Al final muestra un resumen de la sesión

---

## ¿Cómo funciona de manera general?

El sistema tiene tres partes principales que corren al mismo tiempo:

**1. Simulador de mensajes**  
Un hilo independiente genera pedidos aleatorios cada cierto tiempo, como si fueran mensajes llegando por WhatsApp. Cada pedido tiene: nombre del cliente, tipo de rol, cantidad y ubicación de entrega (módulos G, H, M, L, F, cafetería o rectoría).

**2. Cola de pedidos**  
Los pedidos generados se meten a una cola (Queue) que actúa como intermediario entre quien recibe los pedidos y quien los procesa. Esto permite que ambos trabajen a su propio ritmo sin bloquearse entre sí.

**3. Procesador de pedidos**  
Usando un `ThreadPoolExecutor`, varios hilos toman pedidos de la cola y los procesan en paralelo. Cada pedido pasa por dos fases: preparación (limitada por un semáforo) y entrega (con tiempo según la ubicación).

El flujo es así:

```
[WhatsApp simulado] → [Cola de pedidos] → [Pool de hilos] → [Preparación] → [Entrega]
```

---

## ¿Qué cuestiones de concurrencia se implementaron?

### `threading.Thread`
Se usa para correr el simulador de mensajes en un hilo separado al mismo tiempo que el procesador trabaja. Sin esto, primero tendríamos que generar todos los pedidos y luego procesarlos, lo cual no refleja la realidad.

### `ThreadPoolExecutor`
Del módulo `concurrent.futures`. Permite manejar un grupo de hilos de forma ordenada. En lugar de crear y destruir hilos manualmente para cada pedido, el executor los reutiliza. Se configuró con 4 hilos máximos, simulando que hay 4 "repartidores" disponibles.

### `queue.Queue` (Cola thread-safe)
La cola central del sistema. Python ya garantiza que `Queue` es segura para usarse entre hilos, así que varios hilos pueden meter y sacar elementos sin corromperse. Esto evita que dos hilos procesen el mismo pedido al mismo tiempo.

### `threading.Lock`
Se usó en varios lugares:
- Para proteger el contador de pedidos creados (evitar IDs duplicados)
- Para que los mensajes en consola no se mezclen entre hilos
- Para el conteo de pedidos recibidos/procesados en la cola

### `threading.Semaphore`
Se configuró un semáforo con valor 3 para limitar cuántos pedidos se pueden "preparar" al mismo tiempo. Esto simula que el vendedor no puede preparar infinitos roles en paralelo, tiene un límite físico.

### `threading.Event`
Se usa internamente en el simulador para poder detenerlo de forma limpia si fuera necesario, sin matar el hilo a la fuerza.

---

## ¿Para qué sirve?

Sirve para demostrar cómo la programación concurrente puede aplicarse a un problema real: gestionar pedidos que llegan de forma continua sin que se pierdan ni se procesen dos veces.

En un escenario real, este tipo de arquitectura (cola + pool de hilos) es común en sistemas de e-commerce, apps de delivery y cualquier sistema donde lleguen muchas solicitudes al mismo tiempo.

Para el vendedor de roles del CuCEI, representaría pasar de gestionar todo a mano por WhatsApp a tener un sistema que lo hace automáticamente, ordenando los pedidos, asignándolos según disponibilidad y registrando las entregas.

---

## ¿Por qué elegi este proyecto?

Como estudiante que vendo justamente roles dentro del CUGDL la gestión de pedidos por WhatsApp es caótica: se pueden perder mensajes, olvidar pedidos o confundir ubicaciones.

Además, el problema se adapta bien a la concurrencia porque en la vida real los pedidos llegan de forma simultánea e impredecible, exactamente el tipo de escenario donde los hilos tienen sentido.

---

## Motivación personal

La verdad es que al principio no tenia muy claro cómo conectar todos los conceptos del curso (locks, semáforos, ThreadPoolExecutor) en un solo proyecto sin que se sintiera forzado. Pero justo al pensar en los ejemplo que nos llego a poner para explicar la libreria de threading y el hecho de mi emprendimiento se me conecto la idea.

Lo que más me gustó fue ver que el semáforo en la parte de preparación en verdad funcionaba: puedes ver en la salida que nunca hay más de 3 pedidos preparándose al mismo tiempo, aunque haya más en cola. Eso fue satisfactorio porque le da sentido al mecanismo, no solo es código de relleno.

Algo que no pude resolver del todo fue que a veces los prints de distintos hilos se mezclan un poco en consola aunque añadi el Lock. Creo que tiene que ver con el buffering de la terminal, no con el Lock en sí.

---

## Estructura del proyecto

```
roles_cuce/
├── main.py           # Punto de entrada, orquesta todo
├── modelos.py        # Clase Pedido y constantes (tipos, ubicaciones)
├── cola_pedidos.py   # Cola thread-safe con conteo protegido por Lock
├── simulador.py      # Hilo que genera pedidos aleatorios
├── procesador.py     # ThreadPoolExecutor + Semáforo para preparación
└── reporte.py        # Resumen final de la sesión
```

---

## Cómo correr el programa

```bash
# Solo necesitas Python 3, no hay dependencias externas
python main.py
```

Los parámetros configurables están al inicio de `main.py`:

```python
TOTAL_PEDIDOS = 12   # cuántos pedidos genera el simulador
NUM_HILOS = 4        # tamaño del ThreadPoolExecutor
```

---

## Notas finales y cosas que faltaron

- El cálculo de tiempo estimado de entrega es fijo por ubicación. En la versión real dependería de la ubicación actual del vendedor, que lo calcularía un agente externo.
- No se persisten los datos en ningún archivo o base de datos. Todo vive en memoria durante la ejecución.
- El simulador asume que los mensajes de WhatsApp ya vienen parseados (cliente, tipo, cantidad, ubicación). La integración real con la API de WhatsApp Business no está implementada.
- Idealmente, el módulo de reporte podría exportar a un archivo `.txt` o `.csv` al final de cada jornada.
