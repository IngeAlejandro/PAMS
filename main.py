import lexer
import mparser as parser
import objgen

def main():

    print(' ________________________________________ ')
    print('|          ___  ____ _  _ ____           |')
    print('|          |__] |__| |\/| [__            |')
    print('|          |    |  | |  | ___]           |')
    print('|________________________________________|')
    print('|___________v 1.1 (29/10/2019)___________|')
    print('|_____Por: Alejandro Aguilar Frausto_____|')
    print('|________________________________________|')
    
    #------------------------------------
    # Lectura de archivo
    #------------------------------------
    archivoEncontrado = False
    while not archivoEncontrado:
        archivo = input("\nNombre de archivo a traducir (.pams):\n ")
        if not '.pams' in archivo: archivo += '.pams'
        try: 
            with open(archivo, 'r') as file:
                fuente = file.read()
                archivoEncontrado = True
        except: print("Archivo inválido o no encontrado. Verifique que se encuentre entest la carpeta raíz de este script y la extensión '.pams' corresponda.")
    
    print('\n|||||||||||||||||||||    ENTRADA    ||||||||||||||||||||| \n')
    print(fuente)
    print('\n||||||||||||||||||||||||||||||||||||||||||||||||||||||| \n')

    # --------------------------------------
    #  LEXER
    # --------------------------------------

    print('|||||||||||||||||||||  LEXER LOG  ||||||||||||||||||||| \n')

    lex = lexer.Lexer()
    tokens = lex.generarTokens(fuente)
    print(*tokens, sep = "\n")
    print('\n||||||||||||||||||||||||||||||||||||||||||||||||||||||| \n')

    # --------------------------------------
    #  PARSER
    # --------------------------------------

    print('|||||||||||||||||||||  PARSER LOG  |||||||||||||||||||| \n')
    Parser = parser.Parser(tokens)
    source_ast = Parser.parse(tokens)
    print(source_ast) 
    print('\n||||||||||||||||||||||||||||||||||||||||||||||||||||||| \n')

    # --------------------------------------
    # Generacion de Código Traducido
    # --------------------------------------

    generador_codigo = objgen.generadorObjetos(source_ast)
    exec_string = generador_codigo.identifica_objetos()

    # --------------------------------------
    # Salida a Python
    # --------------------------------------

    print('|||||||||||||||||||  CODIGO TRADUCIDO   |||||||||||||||||| \n')
    print(exec_string)
    print('\n|||||||||||||||||||||||||||||||||||||||||||||||||||||||| \n')

    # --------------------------------------
    # Ejecución
    # --------------------------------------

    print('|||||||||||||||||||||||   EJECUCIÓN   |||||||||||||||||||||||| \n')
    exec(exec_string)
    print('\n|||||||||||||||||||||||||||||||||||||||||||||||||||||||| \n')
    
    # --------------------------------------
    # Generacion de archivo de python
    # --------------------------------------

    print('\n|||||||||||||||||||||||||||||||||||||||||||||||||||||||| \n')
    archivo = archivo.replace('.pams', '')
    f = open(archivo + ".py", "w")
    f.write(exec_string)
    f.close()
    print("Archivo '" + archivo + ".py' creado con exito")  
    print('\n|||||||||||||||||||||||||||||||||||||||||||||||||||||||| \n')
    input("")

main()
