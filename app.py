from fastapi import FastAPI, Body
from pydantic import BaseModel
import uvicorn as uv

from ControladorSistema.ControladorSistema import ControladorSistema
from ModuloRed.ModuloRed import ModuloRed
from SIM.SIM import SIM
from SIM.APN import APN

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

# Endpoint to shutdown the raspberry pi
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
@app.get("/wifi-scan")
async def wifi_scan():
    modulo_red = ModuloRed(modo_conexion="wifi")
    estado, mensaje = modulo_red.escanear_redes_wifi()
    return {"estado": estado, "mensaje": mensaje}

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
@app.post("/connect-network")
async def connect_network(request: NetworkIdRequest):
    modulo_red = ModuloRed(modo_conexion="wifi")
    network_id = request.network_id
    estado, mensaje = modulo_red.conectar_a_red_wifi_existente(network_id)
    return {"estado": estado, "mensaje": mensaje}

class WifiConnectionRequest(BaseModel):
    ssid: str
    password: str

@app.post("/wifi-connection") #Para conexiones nuevas
async def wifi_connection(request: WifiConnectionRequest):
    modulo_red = ModuloRed(modo_conexion="wifi")
    ssid = request.ssid
    password = request.password
    estado, mensaje = modulo_red.conectar_red_wifi(ssid, password)
    return {"estado": estado, "mensaje": mensaje}

# Definir un modelo Pydantic para recibir el parámetro como JSON
class NetworkRequest(BaseModel):
    network_id: str

@app.post("/delete-network")
async def eliminar_red(request: NetworkRequest):
    modulo_red = ModuloRed(modo_conexion="wifi")
    estado, mensaje = modulo_red.eliminar_red_wifi(request.network_id)
    return {"estado": estado, "mensaje": mensaje}

'''Para manejar el hotspot'''
#Endpoint para recuperar la información del hotspot
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
    
#Endpoint para conocer que clientes están conectados al AP
@app.get("/connected-clients")
async def connected_clients_info():
    # Crear el objeto de ModuloRed y llamar al método ejecutar_curl
    estado, respuesta = ModuloRed.obtener_clientes_conectados()
    
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
# Endpoint para cambiar la configuración del hotspot
@app.post("/update-hostapd-configuration")
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
@app.post("/apn-configuration")
async def apn_configuration(nombre_apn: str, apn: str, nombre_usuario: str,
                                                    contrasena: str, tipo_apn: str,
                                                    mcc: int, mnc: int):
    apn = APN(nombre_apn, apn, nombre_usuario, contrasena, tipo_apn, mcc, mnc)
    sim = SIM(apn)
    estado, mensaje = sim.cambiar_configuracion_apn()
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


if __name__ == "__main__":
    uv.run(app, host = "0.0.0.0", port = 8000)
