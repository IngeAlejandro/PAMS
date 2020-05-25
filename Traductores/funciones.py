class funciones():

    def __init__(self, ast):

        self.ast = ast['Funcion']
        self.exec_string = ""


    def traducir(self):
        
        for ast in self.ast:

            try:
                if ast['tipo'] == "imprime":
                    self.exec_string += "print("
            except: pass

            # Añade los argumentos a la funcion imprimir
            try: self.exec_string += ast['argumentos'][0] + ")"
            except: pass

        return self.exec_string