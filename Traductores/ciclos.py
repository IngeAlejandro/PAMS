import Traductores.condiciones
from Traductores.variables import variables
from Traductores.funciones import funciones
from Traductores.comentarios import comentarios

class ciclos(object):

	def __init__(self, ast, anidado):
		self.ast = ast['Ciclo']	
		self.exec_string = ""
		self.anidado = anidado


	def traducir(self):

		# Variables con el valor del AST
		nombreValor = ""
		valorInicial = ""
		comparador = ""
		incremento = ""
		valorFinal = ""
		cuerpo = []

		# Loop para guardar las variables
		for val in self.ast:
			try: nombreValor = val['NombreValorInicial']
			except: pass
			try: valorInicial = val['ValorInicial']
			except: pass
			try: comparador = val['Comparacion']
			except: pass
			try: valorFinal = val['ValorFinal']
			except: pass
			try: incremento = val['Incremental']
			except: pass
			try: cuerpo = val['cuerpo']
			except: pass
		# Si el aumnto tiene un + lo elimina (sintáxis de Python)
		if incremento[0] == "+": incremento = incremento[1:len(incremento)]
		# Añade la línea a la sintaxis de Python
		self.exec_string += "for " + nombreValor + " in range(" + str(valorInicial) + ", " + str(valorFinal) + ", " + incremento + "):\n"
		# Añade a la sintaxis de python con identación
		self.exec_string += self.traducir_cuerpo(cuerpo, self.anidado)

		return self.exec_string


	def traducir_cuerpo(self, cuerpo_ast, anidado):
		
		cuerpo_exec_string = ""

		for ast in cuerpo_ast:
			# Parse declaracion
			if self.check_ast('DeclaracionVariable', ast):
				var_obj = variables(ast)
				traducir = var_obj.traducir()
				cuerpo_exec_string += ("   " * anidado) + traducir + "\n"
			# Funciones
			if self.check_ast('Funcion', ast):
				gen_funciones = funciones(ast)
				traducir = gen_funciones.traducir()
				cuerpo_exec_string += ("   " * anidado) + traducir + "\n"
			# Comentarios
			if self.check_ast('Comentario', ast):
				gen_comentario = comentarios(ast)
				traducir = gen_comentario.traducir()
				cuerpo_exec_string += ("   " * anidado) + traducir + "\n"
		
		return cuerpo_exec_string

	
	def check_ast(self, nombreAst, ast):
		try:
			if ast[nombreAst] == []: return True
			if ast[nombreAst]: return True
		except: return False