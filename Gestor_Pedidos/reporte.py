# reporte.py
# Genera un pequeño resumen al final de la ejecucion
# para ver cuantos pedidos se procesaron y de que tipo

from procesador import historial_entregados
from modelos import TIPOS_ROLES, UBICACIONES


def mostrar_resumen(stats_cola):
    #Imprime un resumen de lo que paso en la sesion

    print("\n" + "="*55)
    print("       RESUMEN DE LA SESIÓN - ROLES CUGDL")
    print("="*55)

    print(f"\n  Pedidos recibidos:   {stats_cola['recibidos']}")
    print(f"  Pedidos procesados:  {stats_cola['procesados']}")
    print(f"  En cola aún:         {stats_cola['en_cola']}")

    # Conteo por tipo de rol
    print("\n  Roles vendidos por tipo:")
    conteo_tipo = {t: 0 for t in TIPOS_ROLES}
    total_roles = 0

    for pedido in historial_entregados:
        if pedido.tipo_rol in conteo_tipo:
            conteo_tipo[pedido.tipo_rol] += pedido.cantidad
            total_roles += pedido.cantidad

    for tipo, cantidad in conteo_tipo.items():
        print(f"    - {tipo.capitalize()}: {cantidad} roles")

    print(f"\n  Total de roles vendidos: {total_roles}")

    # Ubicacion mas solicitada
    conteo_ubicacion = {u: 0 for u in UBICACIONES}
    for pedido in historial_entregados:
        if pedido.ubicacion in conteo_ubicacion:
            conteo_ubicacion[pedido.ubicacion] += 1

    if conteo_ubicacion:
        top_ubicacion = max(conteo_ubicacion, key=conteo_ubicacion.get)
        print(f"\n  Ubicacion mas pedida: {top_ubicacion} ({conteo_ubicacion[top_ubicacion]} pedidos)")

    print("\n" + "="*55 + "\n")
