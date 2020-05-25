# Expresiones Regulares
import re

# Mis constantes
import constantes

class Lexer(object):

    def encuentraComillas(self, comillas, indice_actual, codigo_fuente):
        # Si las comillas estan en una sola palabra
        if codigo_fuente[indice_actual].count('"') == 2:
            # Divide el texto
            # ('palabra', 'comillas(")', ';')
            palabra = codigo_fuente[indice_actual].partition(
                '"')[-1].partition('"'[0])
            # regresa la cadena con caracteres depues de las comillas (;)
            if palabra[2] != '':
                return ['"' + palabra[0] + '"', '', palabra[2]]
            # Regresa solo la cadena
            else:
                return ['"' + palabra[0] + '"', '', '']
        else:
            # Elimina lo que se encuentre antes de la comillas
            codigo_fuente = codigo_fuente[indice_actual:len(codigo_fuente)]
            # Almacena y construye el texto
            palabra = ""
            # cuenta las iteraciones
            iteracion = 0
            # recorre hasta encontrar otras comillas
            for item in codigo_fuente:
                iteracion += 1
                # Añade la palabra encontrada
                palabra += item + " "
                # Si la palabra tiene comillas y no es la primera
                if comillas in item and iteracion != 1:
                    # Regresa la cadena, el numero de iteracion y caracteres extra despues de las comillas
                    return [
                        '"' +
                        palabra.partition('"')[-1].partition('"'[0])[0] + '"',
                        palabra.partition('"')[-1].partition('"'[0])[2],
                        iteracion - 1
                    ]
                    # Fin de ciclo al encontrar todo el texto
                    break

    def generarTokens(self, codigo_fuente):
        # Array con los tokens
        tokens = []
        # Separación del código fuente por palabra
        codigo_fuente = codigo_fuente.split()
        indice = 0
        # iteración del código fuente
        while indice < len(codigo_fuente):
            # Guarda las palabras en una variable temporal para guardar en los tokens
            palabra = codigo_fuente[indice]
            # Saltos de línea y los ignora
            if palabra in "\n":
                pass
            #  Tipo de dato
            elif palabra in constantes.TIPOS:
                tokens.append(["TIPO_VARIABLE", palabra])
            # Identificadores
            elif palabra in constantes.CLAVES:
                tokens.append(["ID", palabra])
            # Identifica nombre de variables
            elif re.match("[a-z]", palabra) or re.match("[A-Z]", palabra):
                # Si tiene un salto de línea al final lo elimina
                if palabra[len(palabra) - 1] != ';':
                    tokens.append(["ID", palabra])
                else:
                    tokens.append(["ID", palabra[0:len(palabra) - 1]])
            # Operadores Incrementales
            elif palabra in constantes.OPERADORES_INC:
                tokens.append(['OPERADOR_INCREMENTAL', palabra])
            # operadores
            elif palabra in constantes.OPERADORES:
                tokens.append(["OPERADOR", palabra])
            # Operador de ciclo for
            elif palabra == "::":
                tokens.append(["SEPARADOR", palabra])
            # Comparadores
            elif palabra in constantes.COMPARADORES:
                tokens.append(["COMPARADOR", palabra])
            # Identadores {}
            elif palabra in "{}":
                tokens.append(["IDENTACION", palabra])
            # Comentarios
            elif palabra == "#":
                tokens.append(["COMENTARIO", palabra])
            # Enteros
            elif re.match("[0-9]", palabra) or re.match("[-]?[0-9]", palabra):
                # Si encuentra salto de línea lo elimina
                if palabra[len(palabra) - 1] == ';':
                    tokens.append(["NUMERO", palabra[:-1]])
                else:
                    tokens.append(["NUMERO", palabra])
            # Identifica texto entre comillas
            elif ('"') in palabra:
                # Llama al metodo encuentra comillas para identificar el texto completo
                # Pasa el indice de la palabra con comillas
                comillasReturn = self.encuentraComillas(
                    '"', indice, codigo_fuente)
                # Si se encuentra en la misma palabra solo se añade
                if comillasReturn[1] == '':
                    tokens.append(["TEXTO", comillasReturn[0]])
                # Si la palabra se encuentra en multiples palabras (ej. "Hola mundo")
                else:
                    # Añade el token
                    tokens.append(["TEXTO", comillasReturn[0]])
                    # Si encontro salto de línea al final
                    if ';' in comillasReturn[1]:
                        tokens.append(["FIN_LINEA", ";"])
                    # Aumenta el numero de iteraciones al indice para no duplicar
                    indice += comillasReturn[2]
                    # Salta el resto de condiciones y sigue iterando
                    pass
            # Salto de línea ';'
            if ";" in palabra[len(palabra) - 1]:
                tokens.append(["FIN_LINEA", ";"])

            indice += 1

        return tokens
