# modelos.py
# Aqui definimos las estructuras de datos que usa el sistema
# es como el "esqueleto" de un pedido

import time

TIPOS_ROLES = ["canela", "pizza", "frutos rojos"]

UBICACIONES = [
    "modulo G",
    "modulo H",
    "modulo M",
    "modulo L",
    "modulo F",
    "cafeteria",
    "rectoria"
]

# Tiempos estimados de entrega en minutos segun ubicacion
# son aproximados, en la vida real esto lo calcularía el agente
TIEMPOS_ENTREGA = {
    "modulo G": 5,
    "modulo H": 7,
    "modulo M": 6,
    "modulo L": 8,
    "modulo F": 4,
    "cafeteria": 10,
    "rectoria": 12
}


class Pedido:
    """
    Representa un pedido individual de roles.
    Guarda toda la info que llega (simulada) del WhatsApp.
    """

    _contador = 0  # para generar IDs unicos, aunque no es thread-safe sin lock
                   # (el lock lo manejamos desde afuera en el simulador)

    def __init__(self, cliente, tipo_rol, cantidad, ubicacion):
        Pedido._contador += 1
        self.id = Pedido._contador
        self.cliente = cliente
        self.tipo_rol = tipo_rol
        self.cantidad = cantidad
        self.ubicacion = ubicacion
        self.tiempo_estimado = TIEMPOS_ENTREGA.get(ubicacion, 10)
        self.estado = "pendiente"   # pendiente -> en_proceso -> entregado
        self.timestamp = time.time()

    def __str__(self):
        return (
            f"[Pedido #{self.id}] {self.cliente} | "
            f"{self.cantidad}x rol de {self.tipo_rol} | "
            f"Ubicacion: {self.ubicacion} | "
            f"ETA: ~{self.tiempo_estimado} min | "
            f"Estado: {self.estado}"
        )
