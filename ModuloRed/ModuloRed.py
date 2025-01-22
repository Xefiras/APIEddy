import subprocess
from ModuloRed.Red import Red


class ModuloRed:
    def __init__(self, modo_conexion):
        self.modo_conexion = modo_conexion
        self.interfaz_red = self.get_interfaz_red()

    @staticmethod
    def get_interfaz_red():
            return "wlan1"
    
    def escanear_redes_wifi(self):
        try:
            # Usar wlan1 explícitamente para escanear redes Wi-Fi
            redes_wifi_cmd = subprocess.run(
                ['nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY', 'device', 'wifi', 'list', 'ifname', self.interfaz_red],
                capture_output=True, text=True
            )
            if redes_wifi_cmd.returncode != 0:
                return False, f"Error al escanear redes Wi-Fi: {redes_wifi_cmd.stderr.strip()}"
            
            redes_wifi = self.extraer_datos_redes_wifi(redes_wifi_cmd.stdout)
            return True, redes_wifi

        except Exception as e:
            return False, str(e)

    def listar_redes_wifi(self):
        try:
            # Ejecutar el comando usando subprocess
            result = subprocess.check_output(['sudo', 'wpa_cli', '-i', self.interfaz_red, 'list_networks'])
            # Decodificar el resultado y dividir en líneas
            result = result.decode('utf-8').splitlines()

            # Eliminar la primera línea que contiene los encabezados
            result = result[1:]

            # Crear una lista de redes, formateando cada línea
            redes_wifi = []
            for linea in result:
                # Separar por tabulaciones
                partes = linea.split('\t')
                if len(partes) >= 4:
                    # Extraer los valores
                    red = {
                        "network_id": partes[0],
                        "ssid": partes[1],
                        "bssid": partes[2] if len(partes) > 2 else "any",  # Si no hay BSSID, poner "any"
                        "flags": partes[3]
                    }
                    redes_wifi.append(red)

            return True, redes_wifi
        except subprocess.CalledProcessError as e:
            return False, str(e)

    @staticmethod
    def extraer_datos_redes_wifi(redes_wifi_crudas):
        redes_wifi = redes_wifi_crudas.strip().split('\n')
        lista_redes = []

        for red_wifi in redes_wifi:
            datos_red = red_wifi.split(':')
            if len(datos_red) >= 3 and datos_red[0]:
                lista_redes.append(Red(datos_red[0], '', datos_red[1], datos_red[2]))
        return lista_redes
    
    def conectar_red_wifi(self, ssid, password):
        try:
            if not self.interfaz_red:
                return False, "No se pudo identificar la interfaz de red."

            # Listar redes existentes
            result = subprocess.run(
                ["sudo", "wpa_cli", "-i", self.interfaz_red, "list_networks"],
                capture_output=True, text=True
            )
            networks = result.stdout.splitlines()
            
            # Buscar si ya existe una red con el SSID proporcionado
            netid = None
            for line in networks[1:]:  # Ignorar la primera línea (encabezados)
                columns = line.split("\t")
                if len(columns) > 1 and columns[1] == ssid:
                    netid = columns[0]  # Obtener el ID de la red existente
                    break
           
            # Si no existe, agregar una nueva red
            if netid is None:
                netid = subprocess.run(
                    ["sudo", "wpa_cli", "-i", self.interfaz_red, "add_network"],
                    capture_output=True, text=True
                ).stdout.strip()

                if not netid.isdigit():
                    return False, f"Error al agregar red: {netid}"

                # Configurar el SSID
                subprocess.run(["sudo", "wpa_cli", "-i", self.interfaz_red, "set_network", netid, "ssid", f'"{ssid}"'], check=True)

                # Configurar la contraseña (PSK)
                subprocess.run(["sudo", "wpa_cli", "-i", self.interfaz_red, "set_network", netid, "psk", f'"{password}"'], check=True)

            # Habilitar la red
            subprocess.run(["sudo", "wpa_cli", "-i", self.interfaz_red, "enable_network", netid], check=True)

            # Seleccionar la red recién agregada
            subprocess.run(["sudo", "wpa_cli", "-i", self.interfaz_red, "select_network", netid], check=True)

            # Guardar la configuración
            #print("Guardando Configuración")
            #subprocess.run(["sudo", "wpa_cli", "-i", self.interfaz_red, "save_config"], check=True)

            return True, "Conexión exitosa"

        except subprocess.CalledProcessError as e:
            return False, f"Error al conectar: {e}"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def verificar_red_existente(ssid):
        try:
            with open("/etc/wpa_supplicant/wpa_supplicant.conf", "r") as file:
                return ssid in file.read()
        except FileNotFoundError:
            return False
        except Exception as e:
            return False
    
    def eliminar_red_wifi(self, network_id):
            try:
                # Ejecutar el comando para eliminar la red Wi-Fi
                result = subprocess.run(
                    ["sudo", "wpa_cli", "-i", self.interfaz_red, "remove_network", network_id],
                    capture_output=True, text=True
                )

                if result.returncode != 0:
                    return False, f"Error al eliminar la red: {result.stderr.strip()}"

                return True, f"Red con ID {network_id} eliminada exitosamente"

            except Exception as e:
                return False, str(e)
