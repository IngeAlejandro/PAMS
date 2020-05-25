from Traductores.variables import variables
from Traductores.funciones import funciones
from Traductores.comentarios import comentarios
from Traductores.condiciones import condiciones
from Traductores.ciclos import ciclos

class generadorObjetos():

    def __init__(self, ast_fuente):
        self.ast_fuente = ast_fuente['main_scope']
        # Código a ejecutar
        self.exec_string = ""

    def identifica_objetos(self):
        # Iteración de todo el arbol
        for ast in self.ast_fuente:
            # Declaracion de Variable
            if self.check_ast('DeclaracionVariable', ast):
                gen_var = variables(ast)
                self.exec_string += gen_var.traducir() + '\n'
            # Condicional
            if self.check_ast('Condicional', ast):
                gen_condicion = condiciones(ast, 1)
                self.exec_string += gen_condicion.traducir() + '\n'
            # Funciones
            if self.check_ast('Funcion', ast):
                gen_funcion = funciones(ast)
                self.exec_string += gen_funcion.traducir() + "\n"
            # Comentarios
            if self.check_ast('Comentario', ast):
                gen_comentario = comentarios(ast)
                self.exec_string += gen_comentario.traducir() + "\n"
            # Ciclos
            if self.check_ast('Ciclo', ast):
                gen_ciclo = ciclos(ast, 1)
                self.exec_string += gen_ciclo.traducir() + "\n"

        return self.exec_string

    def check_ast(self, nombreAst, ast):
        try:
            if ast[nombreAst]:
                return True
        except:
            return False
