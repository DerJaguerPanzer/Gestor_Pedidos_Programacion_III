# simulador.py
# Simula la llegada de pedidos como si vinieran del WhatsApp
# En la vida real esto seria el API de WhatsApp mandando los datos

import threading
import time
import random

from modelos import Pedido, TIPOS_ROLES, UBICACIONES

# Nombres de clientes ficticios para la simulacion
CLIENTES = [
    "Ana", "Carlos", "Fer", "Diego", "Lupita",
    "Miguel", "Sofia", "Rodrigo", "Paola", "Ivan",
    "Mariana", "Jorge", "Valeria", "Eduardo", "Daniela"
]

# Usamos un lock para que el contador de Pedido no se corrompa
# cuando varios hilos crean pedidos al mismo tiempo
_lock_contador = threading.Lock()


def generar_pedido_random():
    """Crea un pedido con datos aleatorios como si llegara por WhatsApp"""
    with _lock_contador:
        pedido = Pedido(
            cliente=random.choice(CLIENTES),
            tipo_rol=random.choice(TIPOS_ROLES),
            cantidad=random.randint(1, 5),
            ubicacion=random.choice(UBICACIONES)
        )
    return pedido


class SimuladorMensajes:
    """
    Simula la llegada de mensajes de WhatsApp con pedidos.
    Corre en su propio hilo y va metiendo pedidos a la cola
    cada cierto tiempo.
    """

    def __init__(self, cola, total_pedidos=15, intervalo=0.8):
        self.cola = cola
        self.total_pedidos = total_pedidos
        self.intervalo = intervalo  # segundos entre pedidos
        self._stop_event = threading.Event()
        self._hilo = None

    def _run(self):
        print("\n[Simulador] Empezando a recibir pedidos de WhatsApp...\n")
        enviados = 0

        while enviados < self.total_pedidos and not self._stop_event.is_set():
            pedido = generar_pedido_random()
            if self.cola.agregar_pedido(pedido):
                print(f"  [WA] Nuevo pedido recibido: {pedido}")
                enviados += 1

            # Espera aleatoria para simular que los mensajes no llegan todos juntos
            tiempo_espera = self.intervalo + random.uniform(0, 0.5)
            time.sleep(tiempo_espera)

        print(f"\n[Simulador] Se generaron {enviados} pedidos en total.")

    def iniciar(self):
        self._hilo = threading.Thread(target=self._run, name="SimuladorWA", daemon=True)
        self._hilo.start()

    def esperar(self):
        if self._hilo:
            self._hilo.join()

    def detener(self):
        self._stop_event.set()
