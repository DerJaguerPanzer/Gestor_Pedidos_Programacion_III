# cola_pedidos.py
# Este modulo maneja la cola de pedidos de forma segura entre hilos
# Usa Queue de python que ya es thread-safe, pero igual agregamos
# un Lock para proteger el contador de pedidos activos

import queue
import threading

class ColaPedidos:
    """
    cola central donde se acumulan los pedidos entrantes.
    Varios hilos pueden meter y sacar pedidos al mismo tiempo
    sin que se "pisen" entre ellos.
    """

    def __init__(self, max_pedidos=20):
        # queue.Queue ya es thread-safe por si solo
        self.cola = queue.Queue(maxsize=max_pedidos)

        # Lock para proteger el conteo de pedidos procesados
        self._lock = threading.Lock()
        self.total_recibidos = 0
        self.total_procesados = 0

    def agregar_pedido(self, pedido):
        """
        Mete un pedido a la cola.
        Si la cola esta llena, lo descarta (en produccion se guardaría en BD)
        """
        try:
            self.cola.put_nowait(pedido)
            with self._lock:
                self.total_recibidos += 1
            return True
        except queue.Full:
            print(f"  [ADVERTENCIA] Cola llena, pedido #{pedido.id} descartado por el momento")
            return False

    def obtener_pedido(self, timeout=2):
        """
        Saca el siguiente pedido de la cola.
        Espera hasta 'timeout' segundos si no hay nada.
        """
        try:
            return self.cola.get(timeout=timeout)
        except queue.Empty:
            return None

    def marcar_completado(self):
        """Avisa que un pedido ya se proceso (para el conteo)"""
        self.cola.task_done()
        with self._lock:
            self.total_procesados += 1

    def esta_vacia(self):
        return self.cola.empty()

    def tamanio(self):
        return self.cola.qsize()

    def stats(self):
        with self._lock:
            return {
                "recibidos": self.total_recibidos,
                "procesados": self.total_procesados,
                "en_cola": self.tamanio()
            }
