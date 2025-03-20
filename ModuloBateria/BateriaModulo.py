class BateriaModulo:
    def __init__(self):
        self.carga = self.get_carga()
        self.cargando = self.get_cargando()

    def get_carga(self):
        # TODO some command to get the battery charge
        self.carga = 50
        return self.carga

    def get_cargando(self):
        # TODO some command to get the battery status
        self.cargando = False
        return self.cargando

    def get_status(self):
        return True, [self.get_carga(), self.get_cargando()]
