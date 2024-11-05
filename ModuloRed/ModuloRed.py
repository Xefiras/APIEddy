# Clase encargada de la gestión de las redes wifi y
# red móvil del módulo Eddy

import re
import subprocess


class ModuloRed:
    def __init__(self, modo_conexion):
        self.modo_conexion = modo_conexion
        self.interfaz_red = self.get_interfaz_red()

    @staticmethod
    def get_interfaz_red():
        try:
            interfaz_cmd = subprocess.run(['iwgetid'], capture_output = True, text = True)
            interfaz = interfaz_cmd.stdout.split(' ')
            return interfaz[0]
        except Exception as e:
            return False, str(e)

    # Método para listar las redes wifi
    # que el módulo puede detectar
    # No recibe parámetros
    # Regresa una tupla con
    # un boolean que representa el exito
    # de la funcion y una lista con las redes wifi incluyen su SSID,
    # la intensidad de la señal, y la seguridad
    def listar_redes_wifi(self):
        try:
            redes_wifi_cmd = subprocess.run(['iwlist', self.interfaz_red, 'scan'], capture_output=True, text=True)
            redes_wifi = self.extraer_datos_redes_wifi(redes_wifi_cmd.stdout)

            return True, redes_wifi
        except Exception as e:
            return False, str(e)

    # Método para extraer los datos:
    # SSID
    # Intensidad de la señal
    # Seguridad
    # de las redes wifi mediante Expresiones Regulares
    @staticmethod
    def extraer_datos_redes_wifi(redes_wifi):
        ssid = re.compile("ESSID:.+")
        signal_level = re.compile("Quality=\d\d?/\d{2}")
        security = re.compile("Encryption key:(on|off)")
        lista_redes_wifi = []

        for red in redes_wifi.split("Cell"):
            ssid_red = ssid.findall(red)
            signal_level_red = signal_level.findall(red)
            security_red = security.findall(red)

            if ssid_red or signal_level_red or security_red:
                ssid_red = ssid_red[0].split(":")[1].replace('\"', "")
                # se verifica si el ssid_red ya esta en la lista
                if ssid_red in [red["SSID"] for red in lista_redes_wifi]:
                    continue
                signal_level_red = signal_level_red[0].split("=")[1]
                security_red = security_red[0]
                lista_redes_wifi.append({
                    "SSID": ssid_red,
                    "Signal Level": signal_level_red,
                    "Security": security_red
                })
        return lista_redes_wifi

    # Método para conectar a una red wifi
    # Recibe el SSID y la contraseña de la red wifi
    # y modifica el archivo de configuración de la red wpa_supplicant.conf
    # Regresa una tupla con un boolean que representa
    # el exito de la función y un mensaje
    @staticmethod
    def conectar_red_wifi(ssid, password):
        try:
            if ModuloRed.verificar_red_existente(ssid):
                return False, "La red ya existe en el archivo de configuración"
            red = f'network={{\n\tssid="{ssid}"\n\tpsk="{password}\n\tkey_mgmt=WPA-PSK\n}}\n"'
            with open("/etc/wpa_supplicant/wpa_supplicant.conf", "a") as file:
                file.write(red)

            subprocess.run(['systemctl', 'restart', 'wpa_supplicant'])
            return True, "Conexión exitosa"

        except Exception as e:
            return False, str(e)


    # Método para verificar si la red a agregar ya existe en el archivo wpa_supplicant.conf
    # Recibe el SSID de la red
    # Regresa un boolean que representa si la red ya existe o no
    @staticmethod
    def verificar_red_existente(ssid):
        with open("/etc/wpa_supplicant/wpa_supplicant.conf", "r") as file:
            return ssid in file.read()