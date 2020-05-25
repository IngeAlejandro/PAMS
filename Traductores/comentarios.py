class comentarios():

	def __init__(self, ast):

		self.ast = ast['Comentario']
		self.exec_string = ""

	def traducir(self):
		#genera comentario en sintaxis de python
		self.exec_string += "# " + self.ast
		return self.exec_string