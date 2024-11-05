# Clase encargada de representar
# la configuración de un APN

class APN:
    def __init__(self, nombre_apn, apn, nombre_usuario, contrasena, tipo_apn, mcc, mnc):
        self.nombre_apn = nombre_apn
        self.apn = apn
        self.nombre_usuario = nombre_usuario
        self.contrasena = contrasena
        self.tipo_apn = tipo_apn
        self.mcc = mcc
        self.mnc = mnc