# Clase que controla las operaciones de prendido
# y apagado del módulo Eddy (Raspberry Pi)
import subprocess


class ControladorSistema:
    def __init__(self):
        pass

    # Método para apagar al módulo Eddy
    # No recibe parámetros
    # Regresa una tupla con un booleano que representa
    # el exito de la funcionalidad y un mensaje
    @staticmethod
    def apagar_sistema():
        try:
            subprocess.run(['shutdown', '-h', 'now'])
            return True, "Módulo apagado"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def reiniciar_sistema():
        try:
            subprocess.run(['reboot', '-h', 'now'])
            print("Reiniciando el módulo Eddy...")
            return True, "Reiniciando el módulo Eddy..."
        except Exception as e:
            return False, str(e)  
