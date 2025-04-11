class BateriaModulo:
    def __init__(self):
        self.carga = self.get_carga()
        self.cargando = self.get_cargando()
        self.tiempo_restante = self.get_tiempo_restante()

    def get_carga(self):
        # TODO some command to get the battery charge
        self.carga = 50
        return self.carga

    def get_cargando(self):
        # TODO some command to get the battery status
        self.cargando = False
        return self.cargando

    def get_tiempo_restante(self):
        # TODO some command to get the remaining time
        self.tiempo_restante = 30
        return self.tiempo_restante

    def get_status(self):
        return True, [self.get_carga(), self.get_cargando(), self.get_tiempo_restante()]
