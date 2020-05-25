class variables(object):
    
    def __init__(self, ast):
        # Diccionario
        self.ast = ast['DeclaracionVariable']
        self.exec_string = ""

    
    def traducir(self):        

        for val in self.ast:
            # Nombre
            try: self.exec_string += val['nombre'] + " = "
            except: pass
            # Valor
            try: self.exec_string += str(val['valor'])
            except: pass

        return self.exec_string
