# Clase encargada de la gestión de la SIM del módulo Eddy
import os

class SIM:
    def __init__(self, apn):
        self.apn = apn

    # Método para cambiar la configuración del APN de la SIM
    # Recibe los siguientes parámetros:
    # nombre_apn: str
    # apn: str
    # nombre_usuario: str
    # contrasena: str
    # tipo_apn: str
    # mcc: int
    # mnc: int
    # Regresa una tupla con un boolean que representa el exito
    # de la funcion y un mensaje con la descripción del resultado
    def cambiar_configuracion_apn(self):
        try:
            estado, mensaje = self.validar_apn()
            if not estado:
                return False, mensaje

            comandos = [
                f'AT+CGDCONT=1,"IP","{self.apn.apn}"',
                f'AT+CGAUTH=1,1,"{self.apn.nombre_usuario}","{self.apn.contrasena}"',
                f'AT+COPS=1,2,"{self.apn.mcc}{self.apn.mnc}",7'
            ]

            for comando in comandos:
                resultado = os.popen(f'mmcli -m 0 --command={comando}').read()
                if "error" in resultado:
                    raise Exception(f"Error al ejecutar el comando {comando}")

            # Se reinicia el proceso para aplicar los cambios
            os.system('mmcli -m 0 --reset')

        except Exception as e:
            return False, str(e)


    def validar_apn(self):
        if not self.apn.nombre_apn:
            return False, "El nombre del APN es requerido"
        if not self.apn.apn:
            return False, "El APN es requerido"
        if not self.apn.nombre_usuario:
            return False, "El nombre de usuario es requerido"
        if not self.apn.contrasena:
            return False, "La contraseña es requerida"
        if not self.apn.tipo_apn:
            return False, "El tipo de APN es requerido"
        if not self.apn.mcc:
            return False, "El MCC es requerido"
        if not 0 <= self.apn.mcc < 1000:
            return False, "Valor invalido para el MCC"
        if not self.apn.mnc:
            return False, "El MNC es requerido"
        if not 0 <= self.apn.mnc < 1000:
            return False, "Valor invalido para el MNC"

        return True, "APN válido"