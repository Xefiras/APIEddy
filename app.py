from fastapi import FastAPI
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

# Endpoint to shut down the raspberry pi
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

@app.get("/wifi-list")
async def wifi_list():
    estado, mensaje = ModuloRed.listar_redes_wifi()
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

@app.post("/wifi-connection")
async def wifi_connection(ssid: str, password: str):
    estado, mensaje = ModuloRed.conectar_red_wifi(ssid, password)
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