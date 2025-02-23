# Clase encargada de la representación
# de las redes wifi guardadas en el modulo Eddy

class Red:
    def __init__(self, ssid, fuerza_senal, seguridad, conocida):
        self.ssid = ssid
        self.signal = fuerza_senal
        self.security = seguridad
        self.known = conocida

    def __str__(self):
        return f'SSID: {self.ssid}, Signal: {self.signal}, Seguridad: {self.security}, Conocida: {self.known}'





