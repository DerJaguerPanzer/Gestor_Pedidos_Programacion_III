# procesador.py
# Aqui esta la logica para procesar (preparar y entregar) los pedidos
# Usa ThreadPoolExecutor para manejar varios pedidos a la vez

import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor

# Semaforo que limita cuantos pedidos se pueden "preparar" al mismo tiempo
# porque el vendedor no puede hacer 10 roles a la vez fisicamente
MAX_PREPARACIONES_SIMULTANEAS = 3
semaforo_preparacion = threading.Semaphore(MAX_PREPARACIONES_SIMULTANEAS)

# Lock para imprimir sin que se mezclen los mensajes en consola
_lock_print = threading.Lock()

# Lista compartida con el historial de pedidos entregados
# usamos lock para accederla desde varios hilos
_lock_historial = threading.Lock()
historial_entregados = []


def _imprimir(mensaje):
    """Imprime de forma segura desde cualquier hilo"""
    with _lock_print:
        print(mensaje)


def preparar_pedido(pedido):
    """
    Simula la preparacion del rol.
    El semaforo asegura que no se "preparen" mas de 3 a la vez.
    """
    # Intentamos entrar a la zona de preparacion
    semaforo_preparacion.acquire()
    try:
        _imprimir(f"  [Preparando] Pedido #{pedido.id} de {pedido.cliente} - {pedido.cantidad}x {pedido.tipo_rol}")
        pedido.estado = "en_proceso"

        # Simula el tiempo de preparacion segun cantidad
        tiempo_prep = 1 + (pedido.cantidad * 0.3) + random.uniform(0, 0.5)
        time.sleep(tiempo_prep)

        _imprimir(f"  [Listo para entregar] Pedido #{pedido.id} - tardó {tiempo_prep:.1f}s en prepararse")
    finally:
        semaforo_preparacion.release()


def entregar_pedido(pedido):
    """
    Simula la entrega del pedido en la ubicacion indicada.
    Tarda un tiempo proporcional a la distancia de la ubicacion.
    """
    _imprimir(f"  [En camino] Pedido #{pedido.id} -> {pedido.ubicacion} (ETA: {pedido.tiempo_estimado} min)")

    # Simulamos el tiempo de traslado (reducido para la demo)
    tiempo_traslado = pedido.tiempo_estimado * 0.3 + random.uniform(0, 0.5)
    time.sleep(tiempo_traslado)

    pedido.estado = "entregado"
    _imprimir(f"  [Entregado ✓] Pedido #{pedido.id} entregado a {pedido.cliente} en {pedido.ubicacion}")

    with _lock_historial:
        historial_entregados.append(pedido)


def procesar_pedido_completo(pedido):
    """
    Flujo completo: preparar y luego entregar.
    Esta funcion es la que ejecuta cada hilo del pool.
    """
    preparar_pedido(pedido)
    entregar_pedido(pedido)
    return pedido.id


class ProcesadorPedidos:
    """
    Gestiona el procesamiento de pedidos usando un pool de hilos.
    Lee de la cola y despacha cada pedido a un hilo disponible.
    """

    def __init__(self, cola, num_hilos=4):
        self.cola = cola
        self.num_hilos = num_hilos
        self._activo = True
        self._evento_fin = threading.Event()

    def iniciar(self, total_esperado):
        """
        Arranca el procesador.
        'total_esperado' es cuantos pedidos esperamos recibir en total
        para saber cuando parar.
        """
        procesados = 0

        with ThreadPoolExecutor(max_workers=self.num_hilos, thread_name_prefix="Procesador") as executor:
            futures = []

            while procesados < total_esperado:
                pedido = self.cola.obtener_pedido(timeout=3)

                if pedido is None:
                    # Si no llego nada en el timeout, revisamos si ya terminamos
                    if self.cola.tamanio() == 0 and procesados > 0:
                        break
                    continue

                # Mandamos el pedido a un hilo del pool
                future = executor.submit(procesar_pedido_completo, pedido)
                futures.append(future)
                self.cola.marcar_completado()
                procesados += 1

            # Esperamos que todos los hilos terminen
            for f in futures:
                try:
                    f.result()
                except Exception as e:
                    print(f"  [ERROR] Algo salio mal procesando un pedido: {e}")

        self._evento_fin.set()
        print(f"\n[Procesador] Todos los pedidos fueron atendidos.")

    def esperar_fin(self):
        self._evento_fin.wait()
