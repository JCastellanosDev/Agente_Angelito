from angelito.vector_store import indexar_codigo_local


def cargar_proyectos_ejemplo() -> None:
    print("Iniciando indexacion de archivos de codigo...")

    indexar_codigo_local(
        "RestauranteController.java",
        """
package com.jcastellanosdev.restaurant;

public class RestauranteController {
    public void crearPedido(int mesaId, String platillo, int cantidad) {
        System.out.println("Pedido recibido para la mesa: " + mesaId);
        System.out.println("Platillo: " + platillo + " x" + cantidad);
    }
}
""",
    )

    indexar_codigo_local(
        "redes_config.py",
        """
import os

def configurar_ip_estatica(interfaz, ip, gateway):
    print(f"Configurando interfaz {interfaz} con la IP {ip}...")
    os.system(f"sudo ip addr add {ip}/24 dev {interfaz}")
    os.system(f"sudo ip route add default via {gateway}")
""",
    )

    print("Indexacion completada.")


if __name__ == "__main__":
    cargar_proyectos_ejemplo()
