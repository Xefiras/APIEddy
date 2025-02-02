from fastapi import FastAPI, Body
from pydantic import BaseModel
import uvicorn as uv

from ControladorSistema.ControladorSistema import ControladorSistema
from ModuloRed.ModuloRed import ModuloRed

app = FastAPI()

# Endpoint to shut down the raspberry pi
# response form:
# {
#   "status": "success" | "error",
#   "message": "Apagando el módulo Eddy..." | "Error message"
# }
@app.get("/shutdown")
async def shutdown():
    estado, mensaje = ControladorSistema.apagar_sistema()
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
    
# Endpoint to reboot the raspberry pi
# TODO
@app.get("/reboot")
async def reboot():
    estado, mensaje = ControladorSistema.reiniciar_sistema()
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

'''Para manejar las conexiones wifi'''
# Endpoint to scan for available Wi-Fi networks around
# the Eddy module
# response form:
# {
#   "status": "success" | "error",
#   "networks": [ { "ssid": "network_name", "signal": "signal_strength", "security": "security_type" } ] | "Error message"
# }
@app.get("/wifi-scan")
async def wifi_scan():
    modulo_red = ModuloRed(modo_conexion="wifi")
    estado, response = modulo_red.escanear_redes_wifi()

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
    network_id: str

# Endpoint para conectarse a una red Wi-Fi existente de acuerdo al ID de red
# TODO
@app.post("/connect-network")
async def connect_network(request: NetworkIdRequest):
    modulo_red = ModuloRed(modo_conexion="wifi")
    network_id = request.network_id
    estado, mensaje = modulo_red.conectar_a_red_wifi_existente(network_id)
    return {"estado": estado, "mensaje": mensaje}

class WifiConnectionRequest(BaseModel):
    ssid: str
    password: str

# endpoint to connect to a new Wi-Fi network
# response form:
# {
#   "status": "success" | "error",
#   "message": "Connection successful" | "Error message"
# }
@app.post("/wifi-connection") #Para conexiones nuevas
async def wifi_connection(request: WifiConnectionRequest):
    modulo_red = ModuloRed(modo_conexion="wifi")
    ssid = request.ssid
    password = request.password
    estado, mensaje = modulo_red.conectar_red_wifi(ssid, password)

    if estado:
        return {"status": "success", "message": mensaje}
    else:
        return {"status": "error", "message": mensaje}


# Definir un modelo Pydantic para recibir el parámetro como JSON
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
    # Crear el objeto de ModuloRed y llamar al método ejecutar_curl
    estado, response = ModuloRed.obtener_clientes_conectados()

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
    
# Endpoint para cambiar la configuración del hotspot
# TODO
@app.put("/update-hostapd-configuration")
async def update_hostapd_configuration(
    ssid: str = Body(...), 
    wpa_passphrase: str = Body(...)
):
    estado, mensaje = ModuloRed.editar_hostapd(ssid, wpa_passphrase)
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
    estado, mensaje = ModuloRed.editar_wvdial(config.apn, config.username, config.password)
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
    
# endpoint to update the connection mode (mobile or Wi-Fi)
# response form:
# {
#   "status": "success" | "error",
#   ""message": ""Modo de conexión actualizado a:" + mode" |"Error message"
# }
@app.put("/toggle-ppp-connection")
async def toggle_ppp_connection():
    estado, mensaje = ModuloRed.toggle_ppp_connection()
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
async def general_status():
    # estado, mensaje = ModuloRed.get_general_status() TODO
    estado = True
    data = {
        "connection_mode": "Mobile",
        "status": {
            "name": "Blasfemia",
            "signal": 70
        },
        "battery_level": 2
    }
    errorMessage = "ALGO NO FUNCIONAAAA"
    if estado:
        return {
            "status": "success",
            "data": data
        }
    else:
        return {
            "status": "error",
            "message": errorMessage
        }


if __name__ == "__main__":
    uv.run(app, host = "0.0.0.0", port = 8000)
