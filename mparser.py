
import constantes


class Parser(object):
    def __init__(self, lista_tokens):
        # Indicie de los tokens
        self.token_ind = 0
        # Lista de todos los tokens
        self.lista_tokens = lista_tokens
        # Abstract Syntax tree
        self.ast_fuente = {'main_scope': []}
        # Tabla de símbolos para análisis sintáctico
        self.arbol_simbolos = []
        # Indice de línea
        self.lin_id = 1

    def parse(self, lista_tokens):

        while self.token_ind < len(lista_tokens):
            # Guarda el tipo de token (identificador)
            tipo_token = lista_tokens[self.token_ind][0]
            # Guarda el valor del token
            valor_token = lista_tokens[self.token_ind][1]
            # Procesa declaración de variable
            if tipo_token == "TIPO_VARIABLE":
                self.lin_id += 1
                self.parse_declaracion(
                    lista_tokens[self.token_ind:len(lista_tokens)], False)
            # Procesa patrón para if
            elif tipo_token == "ID" and valor_token == "si":
                self.lin_id += 1
                self.parse_condicional(
                    lista_tokens[self.token_ind:len(lista_tokens)], False)
            # Procesa patrón para 'para'
            elif tipo_token == "ID" and valor_token == "para":
                self.lin_id += 1
                self.parse_ciclo(
                    lista_tokens[self.token_ind:len(lista_tokens)], False)
            # Procesa funciones
            elif tipo_token == "ID" and valor_token in constantes.FUNCIONES:
                self.lin_id += 1
                self.parse_funciones(
                    lista_tokens[self.token_ind:len(lista_tokens)], False)
            # Patrón para comentarios
            elif tipo_token == "COMENTARIO" and valor_token == "#":
                self.lin_id += 1
                self.parse_comentarios(
                    lista_tokens[self.token_ind:len(lista_tokens)], False)

            self.token_ind += 1

        return self.ast_fuente

    def parse_ciclo(self, lista_tokens, esCuerpo):

        ast = {'Ciclo': []}
        tokens_revisados = 1
        seccionLoop = 1

        while tokens_revisados < len(lista_tokens):
            # Si se encuentra el token { termina el ciclo}
            if lista_tokens[tokens_revisados][1] == '{':
                break
            if tokens_revisados == 1:
                # Toma los tokens antes de '::'
                tokens_declaracion = self.encuentra_simbolos(
                    "::", '{', lista_tokens[tokens_revisados:len(lista_tokens)])

                # Error si no encuentra el token '::'
                if tokens_declaracion == False:
                    self.regresar_error(
                        "Falta el operador '::'", lista_tokens)

                # Añade salto de linea para poder tratar la declaracion de variable
                tokens_declaracion[0].append(['FIN_LINEA', ';'])
                parse_var = self.parse_declaracion(
                    tokens_declaracion[0], True)
                # Añade el nombre (variable) al arbol de loop
                # Llamada a la declaracion de variable con valor de false para en cuerpo para no ser añadida al arbol fuente
                ast['Ciclo'].append(
                    {'NombreValorInicial': parse_var[0]['DeclaracionVariable'][1]['nombre']})
                # Añade el valor inicial
                ast['Ciclo'].append(
                    {'ValorInicial': parse_var[0]['DeclaracionVariable'][2]['valor']})
                # Aumenta los tokens, -1 por el token de fin de linea añadido manualmente
                self.token_ind -= tokens_declaracion[1]

            if lista_tokens[tokens_revisados][1] == '::':
                # Siguiente seccion del loop (comparacion)
                if seccionLoop == 1:
                    tokens_condicionales = self.encuentra_simbolos(
                        '::', '{', lista_tokens[tokens_revisados + 1:len(lista_tokens)])
                    ast['Ciclo'].append(
                        {'Comparacion': tokens_condicionales[0][1][1]})
                    ast['Ciclo'].append(
                        {'ValorFinal': tokens_condicionales[0][1][1]})
                    tokens_revisados += tokens_condicionales[1]

                # Siguiente seccion (incremental)
                if seccionLoop == 2:
                    tokens_incrementales = self.encuentra_simbolos(
                        '{', '}', lista_tokens[tokens_revisados + 1:len(lista_tokens)])
                    ast['Ciclo'].append(
                        {'Incremental': self.assemble_token_values(tokens_incrementales[0])})
                    tokens_revisados += tokens_incrementales[1]

                seccionLoop += 1

            tokens_revisados += 1

        self.token_ind += tokens_revisados

        # Toma los tokens del cuerpo y añade 1 para seguir iterando
        tokens_cuerpo = self.forma_linea(
            lista_tokens[tokens_revisados + 1:len(lista_tokens)])

        if not esCuerpo:
            self.parse_cuerpo(tokens_cuerpo[0], ast, 'Ciclo', False)
        else:
            self.parse_cuerpo(tokens_cuerpo[0], ast, 'Ciclo', True)

        tokens_revisados += tokens_cuerpo[1]

        return [ast, tokens_revisados]

    def assemble_token_values(self, tokens):
        attached_tokens = ""
        for token in tokens:
            attached_tokens += token[1] + ""
        return attached_tokens

    # Función para encontrar patrón de simbolos en los tokens
    def encuentra_simbolos(self, simbolo, simbolo_cierre, lista_tokens):

        tokens = []
        tokens_revisados = 0

        for token in lista_tokens:
            tokens_revisados += 1
           # Si encuentra el cierre correspondiente regresa falso (se encontró todo)
            if token[1] == simbolo_cierre:
                return False
            # Si encuentra el símbolo inicial regresa los tokens que se encuentran antes
            if token[1] == simbolo:
                return [tokens, tokens_revisados - 1]
            # Si no añade los tokens a la variable
            else:
                tokens.append(token)
        # Regresa falso si no se encuentra ninguno de los simbolos
        return False

    def parse_comentarios(self, lista_tokens, enCuerpo):

        ast = {'Comentario': ""}
        tokens_revisados = 0
        cadena_comentario = ""

        for token in range(0, len(lista_tokens)):
            # Si encuentra el token de cierre de comentario termina el ciclo
            if lista_tokens[token][0] == "COMENTARIO" and token != 0:
                break
            # Agrega las palabras a la cadena de comentarios
            if token != 0:
                cadena_comentario += str(lista_tokens[token][1]) + " "
            tokens_revisados += 1
        # Agrega el comentario al arbol
        ast['Comentario'] = cadena_comentario

        if not enCuerpo:
            self.ast_fuente['main_scope'].append(ast)

        self.token_ind += tokens_revisados

        return [ast, tokens_revisados]

    def parse_funciones(self, lista_tokens, esCuerpo):

        ast = {'Funcion': []}
        tokens_revisados = 0

        for token in range(0, len(lista_tokens)):
            # Fin de ciclo si encuentra fin de linea
            if lista_tokens[token][0] == "FIN_LINEA":
                break
            # Toma el nombre de la funcion
            if token == 0:
                ast['Funcion'].append({'tipo': lista_tokens[token][1]})
            # Toma el parámetro
            if token == 1 and lista_tokens[token][0] in ['NUM', 'TEXTO', 'ID']:
                # Si es variable (id) toma el valor
                if lista_tokens[token][0] == 'ID':
                    # Toma el valor o manda error
                    valor = self.tomar_valor(lista_tokens[token][1])
                    if valor != False:
                        ast['Funcion'].append({'argumentos': [valor]})
                    else:
                        self.regresar_error(
                            "La variable '%s' no ha sido definida" % lista_tokens[tokens_revisados][1], lista_tokens[0:tokens_revisados + 1])
                else:
                    if lista_tokens[token + 1][0] == 'FIN_LINEA':
                        ast['Funcion'].append(
                            {'argumentos': [lista_tokens[token][1]]})
                    else:
                        llamada_lista_funciones = self.lista_valores(
                            lista_tokens[tokens_revisados:len(lista_tokens)])
                        print(llamada_lista_funciones)
            # Error si no es un tipo válido
            elif token == 1 and lista_tokens[token][0] not in ['NUM', 'TEXTO', 'ID']:
                self.regresar_error("Argumento inválido %s espera cadena de texto o variable" % lista_tokens[token][0],
                                    lista_tokens[0:tokens_revisados + 1])

            tokens_revisados += 1

        if not esCuerpo:
            self.ast_fuente['main_scope'].append(ast)

        self.token_ind += tokens_revisados

        return [ast, tokens_revisados]

    def parse_declaracion(self, lista_tokens, esCuerpo):

        ast = {'DeclaracionVariable': []}
        tokens_revisados = 0
        existe_variable = True

        for x in range(0, len(lista_tokens)):

            tipo_token = lista_tokens[x][0]
            valor_token = lista_tokens[x][1]

            # Salta el '=' en la declaración
            if x == 2 and tipo_token == "OPERADOR" and valor_token == "=":
                pass
            # Regresa error si no hay '=' en la declaración
            if x == 2 and tipo_token != "OPERADOR" and valor_token != "=":
                self.regresar_error("Declaracion sin simbolo de asignacion '='.",
                                    self.lista_tokens[self.token_ind:self.token_ind + tokens_revisados + 2])
            # Si se encuentra salto de línea termina el ciclo
            if lista_tokens[x][0] == "FIN_LINEA":
                break
            # Toma el primer token, el tipo de token
            if x == 0:
                ast['DeclaracionVariable'].append({"tipo": valor_token})
            # Toma la siguiente variable, nombre de la variable
            if x == 1 and tipo_token == "ID":
                # Revisa si el nombre de la variable ha sido usado y regresa error
                if self.tomar_valor(valor_token) != False:
                    self.regresar_error("La variable '%s' ya ha sido definida" % valor_token,
                                        self.lista_tokens[self.token_ind:self.token_ind + tokens_revisados + 1])
                else:
                    existe_variable = False
                    # Revisa si la variable es definida sin asignación
                    if lista_tokens[x + 1][0] == "FIN_LINEA":
                        # Agergar el valor indefinido y termina el loop
                        ast['DeclaracionVariable'].append(
                            {"nombre": valor_token})
                        ast['DeclaracionVariable'].append(
                            {"valor": '"indefinido"'})
                        tokens_revisados += 1
                        break
                    # Si esta definida la añade al arbol de sintaxis
                    else:
                        ast['DeclaracionVariable'].append(
                            {"nombre": valor_token})
            # Error si el nombre corresponde a otro tipo de token (palabra reservada)
            if x == 1 and tipo_token != "ID":
                self.regresar_error("Nombre de Variable '%s' no válido" % valor_token,
                                    self.lista_tokens[self.token_ind:self.token_ind + tokens_revisados + 1])
            # Toma el 3er token, valor de la variable
            if x == 3 and lista_tokens[x + 1][0] == "FIN DE LINEA":
                # Revisa si el valor corresponde al tipo de variable
                if type(eval(valor_token)) == eval(lista_tokens[0][1]):
                    # Si es un numero lo añade como float sino lo añade como cadena de texto
                    try:
                        ast['DeclaracionVariable'].append(
                            {"valor": float(valor_token)})
                    except ValueError:
                        ast['DeclaracionVariable'].append(
                            {"valor": valor_token})
                else:
                    self.regresar_error("El valor no corresponde al tipo de variable",
                                        self.lista_tokens[self.token_ind:self.token_ind + tokens_revisados + 1])
            # Procesa variables con operaciones aritméticas o cocaetnación
            elif x >= 3:
                # Llama la lista de valores y regresa la concatenacion y el numero de tokens revisados
                llamada_lista_funciones = self.lista_valores(
                    lista_tokens[tokens_revisados:len(lista_tokens)])
                lista_valores = llamada_lista_funciones[0]
                tokens_revisados += llamada_lista_funciones[1]
                # Llama la funcion de ecuaciones o concatenacion e intenta añadir el valor
                try:
                    ast['DeclaracionVariable'].append(
                        {"valor": self.parse_ecuaciones(lista_valores)})
                except:
                    try:
                        ast['DeclaracionVariable'].append(
                            {"valor": self.parse_concatenar(lista_valores)})
                    except:
                        self.regresar_error("Declaración de variable inválida",
                                            self.lista_tokens[self.token_ind:self.token_ind + tokens_revisados])
                break

            tokens_revisados += 1

        # Revisa que los elementos de la declaración de variable esten presentes
        try:
            ast['DeclaracionVariable'][0]
        except:
            self.regresar_error("Declaración inválida. No se ha podido definir el TIPO",
                                self.lista_tokens[self.token_ind:self.token_ind + tokens_revisados])
        try:
            ast['DeclaracionVariable'][1]
        except:
            self.regresar_error("Declaración inválida. No se ha podido definir el NOMBRE",
                                self.lista_tokens[self.token_ind:self.token_ind + tokens_revisados])
        try:
            ast['DeclaracionVariable'][2]
        except:
            self.regresar_error("Declaración inválida. No se ha podido definir el VALOR",
                                self.lista_tokens[self.token_ind:self.token_ind + tokens_revisados])

        if not esCuerpo:
            self.ast_fuente['main_scope'].append(ast)

        # Si pasa errores y no existe la variable la añade al arbol de simbolos
        if not existe_variable:
            self.arbol_simbolos.append(
                [ast['DeclaracionVariable'][1]['nombre'], ast['DeclaracionVariable'][2]['valor']])

        self.token_ind += tokens_revisados

        return [ast, tokens_revisados]

    def parse_condicional(self, lista_tokens, anidado):

        tokens_revisados = 0
        ast = {'Condicional': []}

        # Recorre la cadena de un condicional
        for x in range(0, len(lista_tokens)):
            tokens_revisados += 1
            tipo_token = lista_tokens[x][0]
            valor_token = lista_tokens[x][1]

            condionales_permitidos = ['NUMERO', 'TEXTO', 'ID']

            # Termina el loop al final del condicional ({)
            if tipo_token == 'IDENTACION' and valor_token == '{':
                break
            # Salta el if, que ya ha sido identificado
            if tipo_token == 'ID' and valor_token == 'si':
                pass
            # Toma el primer valor y lo añade al arbol
            if x == 1 and tipo_token in condionales_permitidos:
                # Revisa el id de la variable y lo añade al arbol
                if self.tomar_valor(valor_token) != False:
                    ast['Condicional'].append(
                        {'valor1': self.tomar_valor(valor_token)})
                else:
                    ast['Condicional'].append({'valor1': valor_token})
            # Revisa el operador de comparacion
            if x == 2 and tipo_token == 'COMPARADOR':
                ast['Condicional'].append({'tipo_comparador': valor_token})
            # Toma el segundo valor
            if x == 3 and tipo_token in condionales_permitidos:
                # Toma el id de la segunda variable y lo añade al árbol
                if self.tomar_valor(valor_token) != False:
                    ast['Condicional'].append(
                        {'valor2': self.tomar_valor(valor_token)})
                else:
                    ast['Condicional'].append({'valor2': valor_token})

        self.token_ind += tokens_revisados - 1

        # Toma los tokens para formar las lineas de código
        regresa_cuerpo = self.forma_linea(
            lista_tokens[tokens_revisados:len(lista_tokens)])

        # Si esta anidado llama a parse_cuerpo para revisar identacion
        if anidado == True:
            self.parse_cuerpo(regresa_cuerpo[0], ast, 'Condicional', True)
        else:
            self.parse_cuerpo(regresa_cuerpo[0], ast, 'Condicional', False)

        tokens_revisados += regresa_cuerpo[1]

        return [ast, tokens_revisados]

    # Arma el cuerpo anidado en ciclos o condicionales
    def parse_cuerpo(self, lista_tokens, linea, nombreAst, anidado):

        ast = {'cuerpo': []}
        tokens_revisados = 0
        ind_anidado = 0
        # Loop para encontrar el patrón
        while tokens_revisados < len(lista_tokens):
            # Parse declaracion de variable
            if lista_tokens[tokens_revisados][0] == "TIPO":
                parse_declaracion = self.parse_declaracion(
                    lista_tokens[tokens_revisados:len(lista_tokens)], True)
                self.lin_id += 1
                ast['cuerpo'].append(parse_declaracion[0])
                tokens_revisados += parse_declaracion[1]
            # Parse condicional o ciclo anidado
            elif lista_tokens[tokens_revisados][0] == 'ID' and lista_tokens[tokens_revisados][1] == 'si':
                condicional = self.parse_condicional(
                    lista_tokens[tokens_revisados:len(lista_tokens)], True)
                self.lin_id += 1
                ast['cuerpo'].append(condicional[0])
                tokens_revisados += parse_declaracion[1] - 1
            elif lista_tokens[tokens_revisados][0] == "ID" and lista_tokens[tokens_revisados][1] == "para":
                ciclo = self.parse_ciclo(
                    lista_tokens[tokens_revisados:len(lista_tokens)], True)
                self.lin_id += 1
                ast['cuerpo'].append(ciclo[0])
                tokens_revisados += ciclo[1]
            # Parse funciones
            elif lista_tokens[tokens_revisados][0] == 'ID' and lista_tokens[tokens_revisados][1] in constantes.FUNCIONES:
                funciones = self.parse_funciones(
                    lista_tokens[tokens_revisados:len(lista_tokens)], True)
                self.lin_id += 1
                ast['cuerpo'].append(funciones[0])
                tokens_revisados += funciones[1]
            # Parse comentarios
            elif lista_tokens[tokens_revisados][0] == "COMENTARIO" and lista_tokens[tokens_revisados][1] == "#":
                comentarios = self.parse_comentarios(
                    lista_tokens[tokens_revisados:len(lista_tokens)], True)
                self.lin_id += 1
                ast['cuerpo'].append(comentarios[0])
                tokens_revisados += comentarios[1]
            # Aumenta uno cuando encuentra } y lo salta
            if lista_tokens[tokens_revisados][1] == '}':
                ind_anidado += 1

            tokens_revisados += 1
        # Aumenta el indice por la cantidad de tokens de anidación
        self.token_ind += ind_anidado + 1
        # Forma el arbol con la linea completa y el cuerpo unidos
        linea[nombreAst].append(ast)
        # Si no esta anidado se añadde
        if not anidado:
            self.ast_fuente['main_scope'].append(linea)

    def forma_linea(self, lista_tokens):

        ind_anidado = 1
        tokens_revisados = 0
        tokens_cuerpo = []

        for token in lista_tokens:

            tokens_revisados += 1

            valor_token = token[1]
            tipo_token = token[0]

            # Toma los simbolos de identacion { } para aumentar el indice
            if tipo_token == "IDENTACION" and valor_token == "{":
                ind_anidado += 1
            elif tipo_token == "IDENTACION" and valor_token == "}":
                ind_anidado -= 1

            # Si encuentra el cierre } temina de formar el cuerpo
            if ind_anidado == 0:
                tokens_cuerpo.append(token)
                break
            else:
                tokens_cuerpo.append(token)

        return [tokens_cuerpo, tokens_revisados]

    def parse_ecuaciones(self, ecuacion):

        total = 0

        for item in range(0, len(ecuacion)):

            # Toma el primer valor y se añade al total para empezar a hacer el cálculo
            if item == 0:
                total += ecuacion[item]
                pass
            # Revisa todos los operadores y hace la operación correspondiente
            if item % 2 == 1:
                if ecuacion[item] == "+":
                    total += ecuacion[item + 1]
                elif ecuacion[item] == "-":
                    total += ecuacion[item + 1]
                elif ecuacion[item] == "/":
                    total /= ecuacion[item + 1]
                elif ecuacion[item] == "*":
                    total *= ecuacion[item + 1]
                else:
                    self.regresar_error(
                        "Error en ecuación. Operador(es) inválido(s)", ecuacion)
            # Salta los numeros, ya fueron tomados
            elif item % 2 == 0:
                pass

        return total

    def parse_concatenar(self, lista_concatenacion):

        texto_completo = ""

        for item in range(0, len(lista_concatenacion)):

            valor_actual = lista_concatenacion[item]

            # Añade el primer valor al texto
            if item == 0:
                # Revisa si es una variable o texto simple
                # Si es texto lo añade sin comillas
                if valor_actual[0] == '"':
                    texto_completo += valor_actual[1:len(valor_actual) - 1]
                # Si no es texto simple toma el valor de la variable y lo añade a a cadena
                else:
                    valor_variable = self.tomar_valor(valor_actual)
                    if valor_variable != False:
                        texto_completo += valor_variable[1:len(
                            valor_actual) - 1]
                    else:
                        self.regresar_error('No se encuentra la variable "%s" . No ha sido creada' %
                                            lista_concatenacion[item + 1], lista_concatenacion)
                pass

            # Revisa el operador de concatenacion
            if item % 2 == 1:

                if valor_actual == "+":
                    # Revisa si es variable o texto
                    if lista_concatenacion[item + 1][0] != '"':
                        # Toma el valor de la variable y lo añade
                        valor_variable = self.tomar_valor(
                            lista_concatenacion[item + 1])
                        if valor_variable != False:
                            texto_completo += valor_variable[1:len(
                                valor_variable) - 1]
                        else:
                            self.regresar_error('No se encuentra la variable "%s" . No ha sido creada' %
                                                lista_concatenacion[item + 1], lista_concatenacion)
                    else:
                        texto_completo += lista_concatenacion[item +
                                                              1][1:len(lista_concatenacion[item + 1]) - 1]

                elif valor_actual == ";":
                    texto_completo += " " + lista_concatenacion[item + 1]
                # Error en operador
                else:
                    self.regresar_error(
                        "Error en la operacion. Operador inválido", lista_concatenacion)
            # Salta el segundo valor, ya ha sido tomado
            if item % 2 == 0:
                pass

        return '"' + texto_completo + '"'

    def tomar_valor(self, nombre):
        # Toma el valor de la variable del arbol de simbolos
        for var in self.arbol_simbolos:
            if var[0] == nombre:
                return var[1]
        return False

    def lista_valores(self, tokens):
        lista_v = []
        tokens_revisados = 0
        for token in tokens:
            if token[0] == "FIN_LINEA":
                break
            try:
                lista_v.append(int(token[1]))
            except:
                lista_v.append(token[1])
            tokens_revisados += 1

        return [lista_v, tokens_revisados]

    def regresar_error(self, msg, lista_errores):

        print("------------------------ ERROR  ----------------------------")
        print(msg)
        print("Linea: ", (self.lin_id))
        print("------------------------------------------------------------")
        input("")
        quit()
