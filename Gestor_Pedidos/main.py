# main.py
# Punto de entrada del sistema de gestion de pedidos
# Roles CUGDL - Simulador de pedidos concurrentes
#
# Para correr: python main.py

import threading
import time

from cola_pedidos import ColaPedidos
from simulador import SimuladorMensajes
from procesador import ProcesadorPedidos
from reporte import mostrar_resumen

TOTAL_PEDIDOS = 12   # cuantos pedidos va a generar el simulador
NUM_HILOS = 4        # cuantos repartidores virtuales hay


def main():
    print("\n" + "="*55)
    print("   SISTEMA DE PEDIDOS - ROLES CuCEI")
    print("   (Simulacion de pedidos via WhatsApp)")
    print("="*55)
    print(f"\nConfiguracion:")
    print(f"  - Pedidos a simular: {TOTAL_PEDIDOS}")
    print(f"  - Hilos procesadores: {NUM_HILOS}")
    print(f"  - Preparaciones simultaneas max: 3 (semaforo)\n")

    # Inicia la cola compartida entre el simulador y el procesador
    cola = ColaPedidos(max_pedidos=20)

    # Simulador: imita los mensajes de WhatsApp
    simulador = SimuladorMensajes(cola, total_pedidos=TOTAL_PEDIDOS, intervalo=0.6)

    # Procesador: toma los pedidos y los "prepara y entrega"
    procesador = ProcesadorPedidos(cola, num_hilos=NUM_HILOS)

    # Arranca el simulador en su propio hilo
    simulador.iniciar()

    # El procesador corre en el hilo principal pero espera los pedidos
    # Nota: idealmente esto tambien correria en un hilo separado,
    # pero lo dejo asi para simplificar la demo
    hilo_procesador = threading.Thread(
        target=procesador.iniciar,
        args=(TOTAL_PEDIDOS,),
        name="HiloProcesador"
    )
    hilo_procesador.start()

    # Esperamos que ambos terminen
    simulador.esperar()
    hilo_procesador.join()

    # Mostramos el resumen final
    mostrar_resumen(cola.stats())


if __name__ == "__main__":
    main()
