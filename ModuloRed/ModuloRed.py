import subprocess
from ModuloRed.Red import Red


class ModuloRed:
    def __init__(self, modo_conexion):
        self.modo_conexion = modo_conexion
        self.interfaz_red = self.get_interfaz_red()

    @staticmethod
    def get_interfaz_red():
            return "wlan1"

    def listar_redes_wifi(self):
        try:
            # Usar wlan1 explícitamente para listar redes Wi-Fi
            redes_wifi_cmd = subprocess.run(
                ['nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY', 'device', 'wifi', 'list', 'ifname', self.interfaz_red],
                capture_output=True, text=True
            )
            if redes_wifi_cmd.returncode != 0:
                return False, f"Error al listar redes Wi-Fi: {redes_wifi_cmd.stderr.strip()}"
            
            redes_wifi = self.extraer_datos_redes_wifi(redes_wifi_cmd.stdout)
            return True, redes_wifi

        except Exception as e:
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
            print("Guardando Configuración")
            subprocess.run(["sudo", "wpa_cli", "-i", self.interfaz_red, "save_config"], check=True)

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
