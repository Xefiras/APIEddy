import subprocess

import uvicorn as uv
from fastapi import FastAPI
from pydantic import BaseModel

from ControladorSistema.ControladorSistema import ControladorSistema
from ModuloRed.ModuloRed import ModuloRed
from ModuloBateria.BateriaModulo import BateriaModulo

app = FastAPI()

# Endpoint to shut down the raspberry pi
# response form:
# {
#   "status": "success" | "error",
#   "message": "Apagando el módulo Eddy..." | "Error message"
# }
@app.get("/shutdown")
async def shutdown():
    try:
        # Simulación de error de permisos
        raise PermissionError("No tienes permisos suficientes para apagar el sistema.")

        # Simulación de comando no encontrado
        # raise FileNotFoundError("El comando para apagar el sistema no se encontró.")

        # Simulación de apagado exitoso
        estado = True
        mensaje = "Apagando el módulo Eddy..."
        if estado:
            return {
                "status": "success",
                "message": mensaje
            }
        else:
            return {
                "status": "error",
                "message": mensaje
            }

    except PermissionError as e:
        return {
            "status": "error",
            "message": f"Error de permisos, {str(e)}"
        }
    except FileNotFoundError as e:
        return {
            "status": "error",
            "message": f"Error de comando: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error inesperado: {str(e)}"
        }
# Endpoint to reboot the raspberry pi
# TODO
@app.get("/reboot")
async def reboot():
    try:
        # Simulación de error de permisos
        raise PermissionError("No tienes permisos suficientes para reiniciar el sistema.")

        # Simulación de comando no encontrado
        # raise FileNotFoundError("El comando para reiniciar el sistema no se encontró.")

        # Simulación de reinicio exitoso
        estado = True
        mensaje = "Módulo Eddy reiniciado exitosamente, espere un momento..."
        if estado:
            return {
                "status": "success",
                "message": mensaje
            }
        else:
            return {
                "status": "error",
                "message": mensaje
            }

    except PermissionError as e:
        return {
            "status": "error",
            "message": f"Error de permisos, {str(e)}"
        }
    except FileNotFoundError as e:
        return {
            "status": "error",
            "message": f"Error de comando: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error inesperado: {str(e)}"
        }

'''Para manejar las conexiones wifi'''
# Endpoint to scan for available Wi-Fi networks around
# the Eddy module
# response form:
# {
#   "status": "success" | "error",
#   "networks": [ { "ssid": "network_name", "signal": "signal_strength", "security": "security_type", known: Boolean } ] | "Error message"
# }
@app.get("/wifi-scan")
async def wifi_scan():
    try:
        # Simulación de error al ejecutar el comando
        # raise subprocess.CalledProcessError(1, "nmcli", "No se pudo ejecutar el comando nmcli, verifica que estes en el modo Wi-Fi.")

        # Simulación de error de permisos
        # raise PermissionError("No tienes permisos suficientes para escanear redes Wi-Fi.")

        # Simulación de escaneo exitoso
        estado = True
        response = [
            {"ssid": "INFINITUM0962", "signal": "90", "security": "WPA2", "known": True},
            {"ssid": "INFINITUM6EAE", "signal": "80", "security": "WPA3", "known": False}
        ]
        if estado:
            return {
                "status": "success",
                "networks": response
            }
        else:
            return {
                "status": "error",
                "message": response
            }

    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "message": f"{e.output}"
        }
    except PermissionError as e:
        return {
            "status": "error",
            "message": f"Error de permisos: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error inesperado: {str(e)}"
        }

# Endpoint to list the EXISTING Wi-Fi networks saved in
# Eddy module
# TODO
@app.get("/wifi-list")
async def wifi_list_existente():
    modulo_red = ModuloRed(modo_conexion="wifi")
    estado, redes_wifi = modulo_red.listar_redes_wifi()
    if estado:
        return {"status": "success", "networks": redes_wifi}
    else:
        return {"status": "error", "message": redes_wifi}

# Definir el modelo de solicitud
class NetworkIdRequest(BaseModel):
    ssid: str

# Endpoint para conectarse a una red Wi-Fi existente de acuerdo al ID de red
@app.put("/connect-network")
async def connect_network(request: NetworkIdRequest):
    try:
        # Simulación de error al ejecutar el comando
        raise subprocess.CalledProcessError(1, "wpa_cli", "Error al ejecutar el comando wpa_cli.")

        # Simulación de error de permisos
        # raise PermissionError("No tienes permisos suficientes para conectarte a la red Wi-Fi.")

        # Simulación de conexión exitosa
        estado = True
        mensaje = "Conexión exitosa a la red Wi-Fi."
        if estado:
            return {"status": "success", "message": mensaje}
        else:
            return {"status": "error", "message": mensaje}

    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "message": f"Error al ejecutar el comando: {e.cmd}. Activa el modo Wi-Fi."
        }
    except PermissionError as e:
        return {
            "status": "error",
            "message": f"Error de permisos: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error inesperado: {str(e)}"
        }


@app.put("/open-wifi")
async def open_wifi(request: NetworkIdRequest):
    try:
        # Simulación de error al agregar la red
        raise subprocess.CalledProcessError(1, "wpa_cli", "Error al agregar la red Wi-Fi abierta.")

        # Simulación de conexión exitosa
        modulo_red = ModuloRed(modo_conexion="wifi")
        ssid = request.ssid
        estado, mensaje = modulo_red.conectar_red_wifi_abierta(ssid)
        if estado:
            return {"status": "success", "message": mensaje}
        else:
            return {"status": "error", "message": mensaje}

    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "message": f"Error al ejecutar el comando: {e.cmd}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error inesperado: {str(e)}"
        }


class WifiConnectionRequest(BaseModel):
    ssid: str
    password: str

# endpoint to connect to a new Wi-Fi network
# response form:
# {
#   "status": "success" | "error",
#   "message": "Connection successful" | "Error message"
# }
@app.post("/wifi-connection")
async def wifi_connection(request: WifiConnectionRequest):
    try:
        # Simulación de error: la interfaz de red no está disponible
        raise subprocess.CalledProcessError(1, "wpa_cli", "La interfaz wlan1 no está disponible o no está activa")

        # Simulación de conexión exitosa
        modulo_red = ModuloRed(modo_conexion="wifi")
        ssid = request.ssid
        password = request.password
        estado, mensaje = modulo_red.conectar_red_wifi(ssid, password)
        if estado:
            return {"status": "success", "message": mensaje}
        else:
            return {"status": "error", "message": mensaje}

    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "message": f"Error de interfaz: {e.output}, activa el modo Wi-Fi."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error inesperado: {str(e)}"
        }


@app.get("/connetion-status")
async def connection_status(request: NetworkIdRequest):
    modulo_red = ModuloRed(modo_conexion="wifi")
    ssid = request.ssid
    estado, mensaje = modulo_red.obtener_estado_conexion(ssid)
    if estado:
        return {"status": "success", "message": mensaje}
    else:
        return {"status": "error", "message": mensaje}

class NetworkRequest(BaseModel):
    network_id: str

# TODO
@app.post("/delete-network")
async def eliminar_red(request: NetworkRequest):
    modulo_red = ModuloRed(modo_conexion="wifi")
    estado, mensaje = modulo_red.eliminar_red_wifi(request.network_id)
    return {"estado": estado, "mensaje": mensaje}

'''Para manejar el hotspot'''
#Endpoint para recuperar la información del hotspot
# TODO
@app.get("/access-point")
async def access_point_info():
    # Crear el objeto de ModuloRed y llamar al método ejecutar_curl
    estado, respuesta = ModuloRed.obtener_info_ap()
    
    if estado:
        return {
            "status": "success",
            "response": respuesta
        }
    else:
        return {
            "status": "error",
            "message": respuesta
        }
    
# endpoint to get the list of connected clients to the hotspot
# response form:
# {
#   "status": "success" | "error",
#   "clients": [
#       { "name": "client1", "ip": "192.168.0.165" },
#       { "name": "client2", "ip": "192.168.9.10" }
#   ]
# }
@app.get("/connected-clients")
async def connected_clients_info():
    try:
        # Simulación de error al ejecutar el comando curl
        # raise subprocess.CalledProcessError(1, "curl", "No se pudo obtener la lista de clientes conectados. Verifica que el servicio esté activo y accesible.")

        # Simulación de respuesta exitosa
        estado = True
        response = [

        ]

        if estado:
            return {
                "status": "success",
                "clients": response
            }
        else:
            return {
                "status": "error",
                "message": response
            }

    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "message": str(e)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


class HotspotConfiguration(BaseModel):
    ssid: str
    password: str

# endpoint to update the Hotspot configuration
# response form:
# {
#   "status": "success" | "error",
#   ""message": "Hotspot actualizado" | "Error message"
# }
@app.put("/hotspot-configuration")
async def update_hostapd_configuration(config: HotspotConfiguration):
    try:
        # Simulación de error al editar el archivo de configuración
        raise FileNotFoundError("El archivo de configuración hostapd.conf no se encuentra. Verifica que el archivo exista en la ruta esperada.")

        # Simulación de actualización exitosa
        estado = True
        mensaje = "Hotspot actualizado exitosamente"
        if estado:
            return {
                "status": "success",
                "message": mensaje
            }
        else:
            return {
                "status": "error",
                "message": mensaje
            }

    except FileNotFoundError as e:
        return {
            "status": "error",
            "message": f"Error de archivo, {str(e)}"
        }
    except PermissionError as e:
        return {
            "status": "error",
            "message": f"Error de permisos: {str(e)}. Asegúrate de tener los permisos necesarios para modificar el archivo."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error inesperado: {str(e)}"
        }
    
'''Para manejar el módem GSM'''

class APNConfiguration(BaseModel):
    apn: str
    username: str
    password: str

# endpoint to update the APN configuration
# response form:
# {
#   "status": "success" | "error",
#   ""message": "APN configuration updated" | "Error message"
# }
@app.put("/apn-configuration")
async def apn_configuration(config: APNConfiguration):
    try:
        # Simulación de error al editar el archivo wvdial.conf
        raise FileNotFoundError("El archivo wvdial.conf no se encuentra. Verifica que el archivo exista en la ruta esperada: /etc/wvdial.conf.")

        # Simulación de actualización exitosa
        estado = True
        mensaje = "Configuración APN actualizada exitosamente"
        if estado:
            return {
                "status": "success",
                "message": mensaje
            }
        else:
            return {
                "status": "error",
                "message": mensaje
            }

    except FileNotFoundError as e:
        return {
            "status": "error",
            "message": f"Error de archivo, {str(e)}. Asegúrate de que el archivo wvdial.conf esté presente y tenga los permisos adecuados."
        }
    except PermissionError as e:
        return {
            "status": "error",
            "message": f"Error de permisos: {str(e)}. Asegúrate de tener permisos de escritura en el archivo wvdial.conf."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error inesperado: {str(e)}. Verifica la configuración del sistema."
        }
    
# endpoint to update the connection mode (mobile or Wi-Fi)
# response form:
# {
#   "status": "success" | "error",
#   ""message": ""Modo de conexión actualizado a:" + mode" |"Error message"
# }
@app.put("/toggle-ppp-connection")
async def toggle_ppp_connection():
    try:
        # Simulación de error al alternar la conexión
        raise subprocess.CalledProcessError(1, "pgrep", "No se pudo verificar el estado de wvdial. Verifica que la antena este instalada y configurada correctamente.")

        # Simulación de alternancia exitosa
        estado = True
        mensaje = "Modo de conexión actualizado a: Mobile"
        if estado:
            return {
                "status": "success",
                "message": mensaje
            }
        else:
            return {
                "status": "error",
                "message": mensaje
            }

    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "message": f"{e.output}"
        }
    except PermissionError as e:
        return {
            "status": "error",
            "message": f"Error de permisos: {str(e)}. Asegúrate de tener permisos suficientes para alternar la conexión."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error inesperado: {str(e)}. Verifica la configuración del sistema."
        }

# Endpoint para consultar la intensidad de señal
@app.get("/signal-strength")
async def signal_strength(interface: str = "wlan1", port: str = "/dev/serial0"):
    if interface == "wlan1":
        estado, mensaje = ModuloRed.get_wlan_signal_strength(interface)
        return {
            "status": "success" if estado else "error",
            "message": mensaje
        }
    elif interface == "sim7600x":
        return ModuloRed.get_sim7600_signal_strength(port)
    else:
        return {
            "status": "error",
            "message": f"Interfaz no soportada: {interface}. Usa 'wlan1' o 'sim7600x'."
        }

#Endpoint para saber que red se está utilizando
@app.get("/check-network-status")
async def check_network_status():
    estado, mensaje = ModuloRed.obtener_estado_redes()
    return {"estado": estado, "mensaje": mensaje}

# Endpoint for getting the battery status
# response form:
# {
#   "status": "success" | "error",
#   "charge": 50,
#   "charging": false,
#   "remaining_time": 30
# }
@app.get("/battery-status")
async def battery_status():
    try:
        # Simulación de error al obtener el estado de la batería
        raise FileNotFoundError("No se pudo acceder a la información de la batería. Verifica que el módulo esté correctamente conectado.")

        # Simulación de respuesta exitosa
        bateria = BateriaModulo()
        estado, message = bateria.get_status()
        if estado:
            return {
                "status": "success",
                "charge": message[0],
                "charging": message[1],
                "remaining_time": message[2]
            }
        else:
            return {
                "status": "error",
                "message": "No se pudo obtener el estado de la batería."
            }

    except FileNotFoundError as e:
        return {
            "status": "error",
            "message": f"Error de archivo, {str(e)}."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error inesperado: {str(e)}"
        }

# Endpoint to get the principal data of the system
# - Current connection mode and its _status_
#   - _status_: Wi-Fi ssid and signal strength, or mobile network operator and signal strength
# - Battery level
# response form:
# {
#   "status": "success" | "error",
#   "data": {
#       "connection_mode": "Wi-Fi" | "Mobile",
#       "status": {
#           "name": "network_name",
#           "signal": 70
#       },
#       "battery_level": 50
#   }
@app.get("/general-status")
def general_status():
    try:
        # Simulación de error al obtener el estado de la red
        raise FileNotFoundError("No se pudo obtener el estado de la red. Verifica que estes conectado a la red del módulo.")

        # Simulación de estado de red exitoso
        estado_red = True
        mensaje_red = "Wi-Fi"  # Simulando que la red es Wi-Fi

        if not estado_red:
            return {"status": "error", "message": mensaje_red}

        if mensaje_red == "Wi-Fi":
            # Simulación de señal Wi-Fi
            status = True
            signal_info = {
                "ESSID": "INFINITUM0962",
                "Signal Level": 90
            }
            connection_mode = "Wi-Fi"
        else:
            # Simulación de señal móvil
            signal_info = {
                "ESSID": "internet.itelcel.com",
                "Signal Level": 80
            }
            connection_mode = "Mobile"
            status = True

        if not status:
            return {"status": "error", "message": signal_info}

        # Simulación de nivel de batería
        battery_level = 50

        response = {
            "status": "success",
            "data": {
                "connection_mode": connection_mode,
                "status": {
                    "name": signal_info["ESSID"],
                    "signal": signal_info["Signal Level"]
                },
                "battery_level": battery_level
            }
        }

        return response

    except FileNotFoundError as e:
        return {"status": "error", "message": f"{str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Error inesperado: {str(e)}"}

if __name__ == "__main__":
    uv.run(app, host = "0.0.0.0", port = 8000)
