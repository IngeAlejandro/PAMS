from Traductores.variables import variables
from Traductores.funciones import funciones
from Traductores.ciclos import ciclos
from Traductores.comentarios import comentarios

class condiciones():

    def __init__(self, ast, anidado):
        self.ast = ast['Condicional']
        self.exec_string = ""
        self.anidado = anidado


    def traducir(self):

        for val in self.ast:

            try: self.exec_string += "if " + str(val['valor1']) + " "
            except: pass

            try: self.exec_string += val['tipo_comparador'] + " "
            except: pass

            try: self.exec_string += str(val['valor2']) + ": \n"
            except: pass

            try: self.exec_string += self.traducir_body(val['cuerpo'], self.anidado)
            except: pass
        
        return self.exec_string


    def traducir_body(self, body_ast, anidado):

        body_exec_string = ""

        for ast in body_ast:

            if self.check_ast('DeclaracionVariable', ast):
                var_obj = variables(ast)
                traducir = var_obj.traducir()
                body_exec_string += ("   " * anidado) + traducir + "\n"

            if self.check_ast('Funcion', ast):
                gen_funcion = funciones(ast)
                traducir = gen_funcion.traducir()
                body_exec_string += ("   " * anidado) + traducir + "\n"

            if self.check_ast('Comentario', ast):
                gen_comentario = comentarios(ast)
                traducir = gen_comentario.traducir()
                body_exec_string += ("   " * anidado) + traducir + "\n"
        
        return body_exec_string

    
    def check_ast(self, nombreAst, ast):

        try:
            if ast[nombreAst] == []: return True
            if ast[nombreAst]: return True
        except: return False