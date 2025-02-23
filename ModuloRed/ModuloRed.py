import subprocess
import json
import os
import time
from traceback import print_tb

import serial
import re
from ModuloRed.Red import Red


class ModuloRed:

    LOG_FILE_PATH = os.path.join(os.getcwd(), "wvdial_output.log")

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

            # Listar las redes Wi-Fi guardadas en wpa_supplicant
            command = f"wpa_cli -i {self.interfaz_red} list_networks | awk -F '\\t' '{{print $2}}'"

            print("Sacando redes")
            redes_wifi_guardadas = subprocess.run(command, shell=True, capture_output=True, text=True)

            redes_wifi = self.extraer_datos_redes_wifi(redes_wifi_cmd.stdout, redes_wifi_guardadas.stdout)
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
    def extraer_datos_redes_wifi(redes_wifi_crudas, redes_wifi_guardadas_crudas):
        print("limpiando redes")
        redes_wifi = redes_wifi_crudas.strip().split('\n')
        redes_wifi_guardadas = redes_wifi_guardadas_crudas.strip().split('\n')

        lista_redes = []
        for red_wifi in redes_wifi:
            datos_red = red_wifi.split(':')

            if len(datos_red) >= 3 and datos_red[0]:
                conocida = False
                for red_wifi_guardada in redes_wifi_guardadas:
                    if datos_red[0] in red_wifi_guardada:
                        lista_redes.append(Red(datos_red[0], '', datos_red[1], datos_red[2], True))
                        print(f'Conocida: {datos_red[0]}')
                        conocida = True
                        break
                if not conocida:
                    lista_redes.append(Red(datos_red[0], '', datos_red[1], datos_red[2], False))
                    print(f'No conocida: {datos_red[0]}')
        print(f'Lista: {lista_redes}')
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

            # Verificar estado
            status = subprocess.check_output(["sudo", "wpa_cli", "-i", self.interfaz_red, "status"]).decode("utf-8")
            if "wpa_state=COMPLETED" not in status:
                subprocess.run(["sudo", "wpa_cli", "-i", self.interfaz_red, "remove_network", netid], check=True)
                return False, "Verifique las credenciales"

            # Guardar la configuración
            #subprocess.run(["sudo", "wpa_cli", "-i", self.interfaz_red, "save_config"], check=True)

            return True, "Conexión exitosa"

        except subprocess.CalledProcessError as e:
            return False, f"Error al conectar: {e}"
        except Exception as e:
            return False, str(e)

    # Método para conectar a una red Wi-Fi por su ID
    def conectar_a_red_wifi_existente(self, network_id):
        try:
            # Ejecutar el comando para seleccionar la red Wi-Fi
            result = subprocess.run(
                ["sudo", "wpa_cli", "-i", self.interfaz_red, "select_network", network_id],
                capture_output=True, text=True
            )

            if result.returncode != 0:
                return False, f"Error al conectar a la red: {result.stderr.strip()}"

            return True, f"Conexión exitosa a la red con ID {network_id}"

        except Exception as e:
            return False, str(e)
    
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
            
    @staticmethod
    def obtener_info_ap():
        try:
            # Comando curl como una lista
            curl_command = [
                "curl", "-X", "GET",
                "http://10.3.141.1:8081/ap",
                "-H", "accept: application/json",
                "-H", "access_token: x7yszknswp1ecqzusoqcoovy6kfhj5ro"
            ]
            
            # Ejecutar el comando y capturar la salida
            result = subprocess.run(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                # Convertir la salida a JSON si es posible
                try:
                    response_data = json.loads(result.stdout)
                except json.JSONDecodeError:
                    response_data = result.stdout  # Si no es JSON, devolver como texto
                return True, response_data
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)
        
    @staticmethod
    def obtener_clientes_conectados():
        try:
            # Comando curl como una lista
            curl_command = [
                "curl", "-X", "GET",
                "http://10.3.141.1:8081/clients/wlan0",
                "-H", "accept: application/json",
                "-H", "access_token: x7yszknswp1ecqzusoqcoovy6kfhj5ro"
            ]
            
            # Ejecutar el comando y capturar la salida
            result = subprocess.run(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                try:
                    response_data = json.loads(result.stdout)
                    
                    # Procesar clientes si el JSON es válido
                    final_response = [
                        {
                            "name": client.get("hostname", "Unknown"),
                            "ip": client.get("ip_address", "N/A")
                        }
                        for client in response_data.get("active_clients", [])
                    ]
                    return True, final_response
                except json.JSONDecodeError:
                    # Si la salida no es JSON, devolver como texto
                    return False, "La salida no es JSON válido: " + result.stdout
            else:
                return False, "Error al ejecutar curl: " + result.stderr
        except Exception as e:
            return False, f"Error general: {str(e)}"

        
    #Método para modificar la configuración del hotspot, donde al final se debe reiniciar el servicio para aplicar los cambios
    @staticmethod
    def editar_hostapd(ssid: str, wpa_passphrase: str):
        try:
            # Ruta del archivo hostapd.conf
            hostapd_conf_path = "/etc/hostapd/hostapd.conf"

            # Comprobar si el archivo existe
            if not os.path.exists(hostapd_conf_path):
                return False, f"El archivo {hostapd_conf_path} no se encuentra."

            # Leer el contenido del archivo
            with open(hostapd_conf_path, 'r') as f:
                lines = f.readlines()

            # Modificar las líneas correspondientes
            updated = False
            for i, line in enumerate(lines):
                if line.startswith("ssid="):
                    lines[i] = f"ssid={ssid}\n"
                    updated = True
                elif line.startswith("wpa_passphrase="):
                    lines[i] = f"wpa_passphrase={wpa_passphrase}\n"
                    updated = True

            if not updated:
                return False, "No se encontraron las líneas ssid o wpa_passphrase en el archivo."

            # Guardar los cambios en el archivo
            with open(hostapd_conf_path, 'w') as f:
                f.writelines(lines)

            # Reiniciar el servicio hostapd para aplicar los cambios
            restart_command = ["systemctl", "restart", "hostapd"]
            result = subprocess.run(restart_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode != 0:
                return False, f"Error al reiniciar el servicio hostapd: {result.stderr}"

            return True, "Archivo hostapd.conf actualizado correctamente."

        except Exception as e:
            return False, f"Error al editar el archivo: {str(e)}"
        
    #Método para cambiar de modo de conexión, con wvdial (ppp) o Wi-Fi (wlan1)        
    @staticmethod
    def toggle_ppp_connection():
        try:
            # Verificar si el proceso wvdial está en ejecución
            wvdial_running = subprocess.run(
                ["pgrep", "wvdial"], capture_output=True, text=True
            ).returncode == 0
            
            # Ruta donde se guardará el log de la salida de wvdial
            log_file = os.path.join(os.getcwd(), "wvdial_output.log")

            if wvdial_running:
                # Si wvdial está en ejecución, detenerlo y habilitar wlan1
                print("Deteniendo wvdial y habilitando wlan1...")
                subprocess.Popen(["sudo", "poff.wvdial"])

                subprocess.run(["sudo", "ip", "link", "set", "wlan1", "up"], check=True)
                time.sleep(7)
                print("Conexión PPP detenida y wlan1 habilitada.")
                return True, "Wi-Fi"
            else:
                # Si wvdial no está en ejecución, iniciar la conexión PPP en segundo plano
                print("Deshabilitando wlan1 y ejecutando wvdial en segundo plano...")
                                    
                subprocess.run(["sudo", "ip", "link", "set", "wlan1", "down"], check=True)

                while True:
                    # Ejecutar wvdial y guardar salida en log
                    with open(ModuloRed.LOG_FILE_PATH, "w") as log_file:
                        process = subprocess.Popen(
                            ["sudo", "wvdial"],
                            stdout=log_file,
                            stderr=log_file,
                            text=True
                        )

                    # Medir tiempo de ejecución
                    start_time = time.time()
                    while process.poll() is None:  # Mientras el proceso no termine
                        elapsed_time = time.time() - start_time
                        if elapsed_time > 15:  # Si pasa más de 15 segundos, considerar que está funcionando
                            print("Conexión PPP establecida correctamente.")
                            return True, "Mobile"
                        time.sleep(1)  # Esperar un momento antes de verificar nuevamente
                    
                    # Si el proceso termina antes de los 15 segundos, leer el log
                    with open(ModuloRed.LOG_FILE_PATH, "r") as log_file:
                        log_content = log_file.read()

                    if "--> Modem not responding." in log_content:
                        print("El módem no respondió. Intentando nuevamente...")
                        time.sleep(5)  # Esperar antes de reintentar
                    else:
                        print("Conexión PPP establecida correctamente.")
                        return True, "Mobile"

        except subprocess.CalledProcessError as e:
            print(f"Error en la ejecución del comando: {str(e)}")
            return False, f"Error en la ejecución del comando: {str(e)}"
        except Exception as e:
            print(f"Error desconocido: {str(e)}")
            return False, f"Error desconocido: {str(e)}"
    
    @staticmethod
    def editar_wvdial(apn: str, username: str, password: str):
        try:
            # Ruta del archivo wvdial.conf
            wvdial_conf_path = "/etc/wvdial.conf"

            # Comprobar si el archivo existe
            if not os.path.exists(wvdial_conf_path):
                return False, f"El archivo {wvdial_conf_path} no se encuentra."

            # Leer el contenido del archivo
            with open(wvdial_conf_path, 'r') as f:
                lines = f.readlines()

            # Modificar las líneas correspondientes
            updated = False
            for i, line in enumerate(lines):
                if line.startswith("Init3 ="):
                    lines[i] = f'Init3 = AT+CGDCONT=1,"IP","{apn}"\n'
                    updated = True
                elif line.startswith("Username ="):
                    lines[i] = f"Username = {username}\n"
                    updated = True
                elif line.startswith("Password ="):
                    lines[i] = f"Password = {password}\n"
                    updated = True

            if not updated:
                return False, "No se encontraron las líneas Init3, Username o Password en el archivo."

            # Guardar los cambios en el archivo
            with open(wvdial_conf_path, 'w') as f:
                f.writelines(lines)

            return True, "Archivo wvdial.conf actualizado correctamente."

        except Exception as e:
            return False, f"Error al editar el archivo: {str(e)}"

    @staticmethod
    def get_wlan_signal_strength(interface="wlan1"):
        try:
            # RECOMENDATION: YOU CAN USE
            # nmcli -t -f IN-USE,SSID,SIGNAL device wifi list | grep "*" | cut -d: -f 2,3
            # with this, u would see the next output:
            # IZZY12234:100
            # where IZZY12234 is the SSID and 100 is the signal strength
            # result = subprocess.run("nmcli -t -f IN-USE,SSID,SIGNAL device wifi list | grep '*' | cut -d: -f 2,3", shell=True, capture_output=True, text=True)
            result = subprocess.run(["iwconfig", interface], capture_output=True, text=True)

            if result.returncode != 0:
                return False, f"No se pudo obtener la información de {interface}: {result.stderr.strip()}"

            output = result.stdout
            essid_match = re.search(r'ESSID:"(.*?)"', output)
            signal_match = re.search(r'Signal level=(-?\d+) dBm', output)

            signal_info = {
                "ESSID": essid_match.group(1) if essid_match else "Desconocido",
                "Signal Level": int(signal_match.group(1)) if signal_match else 0
            }

            return True, signal_info

        except Exception as e:
            return False, f"Error al obtener la señal de {interface}: {str(e)}"

    @staticmethod
    def get_sim7600_signal_strength(port="/dev/serial0", baudrate=115200):
        """
        Obtiene información de la señal del módulo SIM7600X y la devuelve en un diccionario.
        """
        try:
            with serial.Serial(port, baudrate, timeout=1) as ser:
                # Comando AT+CSQ (Intensidad de señal)
                ser.write(b"AT+CSQ\r")
                time.sleep(0.5)
                response = ser.readlines()

                signal_strength = None
                for line in response:
                    line = line.decode().strip()
                    if line.startswith("+CSQ"):
                        parts = line.split(":")[1].strip().split(",")
                        if len(parts) > 0:
                            rssi = int(parts[0])  # Intensidad de señal
                            if rssi == 99:
                                signal_strength = "Sin señal"
                            else:
                                signal_strength = -113 + (rssi * 2)  # Convertir a dBm

                # Comando AT+CPSI? (Tipo de red, Banda)
                ser.write(b"AT+CPSI?\r")
                time.sleep(0.5)
                response = ser.readlines()

                network_type = "No disponible"
                band = "No disponible"
                for line in response:
                    line = line.decode().strip()
                    if line.startswith("+CPSI"):
                        parts = line.split(":")[1].strip().split(",")
                        if len(parts) > 7:
                            network_type = parts[0].strip()
                            band = parts[7].strip()

                # Comando AT+COPS? (Operador de red)
                ser.write(b"AT+COPS?\r")
                time.sleep(0.5)
                response = ser.readlines()

                carrier = "No disponible"
                for line in response:
                    line = line.decode().strip()
                    if line.startswith("+COPS"):
                        parts = line.split(":")[1].strip().split(",")
                        if len(parts) > 2:
                            carrier = parts[2].strip().replace('"', '')

                # Construir y devolver el JSON
                return {
                    "status": "success",
                    "data": {
                        "signal_strength": signal_strength,
                        "network_type": network_type,
                        "band": band,
                        "carrier": carrier
                    }
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Error al obtener la señal del SIM7600X: {str(e)}"
            }

        
    @staticmethod
    def obtener_estado_redes():
        try:
            # Obtener el estado de las interfaces de red con ifconfig
            result = subprocess.run(["ifconfig"], capture_output=True, text=True)

            if result.returncode != 0:
                return False, "Error al obtener el estado de las interfaces de red."

            # Analizar la salida para ver si las interfaces wlan1 o ppp0 están activas
            output = result.stdout
            if "wlan1" in output and "inet" in output:  # Verifica si wlan1 está activo
                return True, "Wi-Fi"
            elif "ppp0" in output and "inet" in output:  # Verifica si ppp0 está activo
                return True, "Mobile"
            else:
                return False, "Ninguna interfaz de red activa detectada."

        except Exception as e:
            return False, f"Error al obtener el estado de las interfaces de red: {str(e)}"
