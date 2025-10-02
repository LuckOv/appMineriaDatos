import csv
import os

# FUNCIÓN PARA LEER CSV
def csv_a_diccionarios(archivo):
    """
    Lee un archivo CSV y retorna una lista de diccionarios
    """
    try:
        with open(archivo, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return list(reader)
    except FileNotFoundError:
        print(f"Error: El archivo '{archivo}' no existe.")
        return []
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return []

# FUNCIÓN PARA AGREGAR REGISTROS
def agregar_registro(archivo, nuevo_registro):
    """
    Agrega un nuevo registro al archivo CSV
    """
    try:
        # Verificar si el archivo existe para determinar si hay que escribir encabezados
        archivo_existe = os.path.isfile(archivo)
        
        with open(archivo, 'a', newline='', encoding='utf-8') as file:
            campos = nuevo_registro.keys()
            writer = csv.DictWriter(file, fieldnames=campos)
            
            # Escribir encabezados solo si el archivo no existe
            if not archivo_existe:
                writer.writeheader()
            
            writer.writerow(nuevo_registro)
        
        print(f"Registro agregado exitosamente al archivo '{archivo}': {nuevo_registro}")
        return True
    except Exception as e:
        print(f"Error al agregar registro: {e}")
        return False

# FUNCIÓN PARA BORRAR REGISTROS
def borrar_por_indice(archivo, indices):
    """
    Borra registros por sus índices (empezando desde 0)
    indices: lista de índices a borrar
    """
    try:
        if not isinstance(indices, list):
            indices = [indices]
        
        registros_restantes = []
        registros_borrados = 0
        
        with open(archivo, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            encabezados = reader.fieldnames
            registros = list(reader)
        
        # Filtrar por índices
        for i, registro in enumerate(registros):
            if i not in indices:
                registros_restantes.append(registro)
            else:
                registros_borrados += 1
        
        # Escribir de vuelta
        with open(archivo, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=encabezados)
            writer.writeheader()
            writer.writerows(registros_restantes)
        
        print(f"Se borraron {registros_borrados} registros del archivo '{archivo}'")
        return registros_borrados
    except FileNotFoundError:
        print(f"Error: El archivo '{archivo}' no existe.")
        return 0
    except Exception as e:
        print(f"Error al borrar registros: {e}")
        return 0

# FUNCIÓN PARA MODIFICAR REGISTROS
def modificar_interactivo(archivo):
    """
    Función interactiva para modificar registros
    """
    try:
        if not os.path.exists(archivo):
            print(f"Error: El archivo '{archivo}' no existe")
            return False
        
        # Leer registros
        with open(archivo, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            encabezados = reader.fieldnames
            registros = list(reader)
        
        if not registros:
            print("El archivo no contiene registros")
            return False
        
        # Mostrar registros
        print(f"\n--- REGISTROS EXISTENTES EN '{archivo}' ---")
        for i, registro in enumerate(registros):
            print(f"{i}: {registro}")
        
        # Seleccionar registro
        try:
            indice = int(input("\nIngrese el índice del registro a modificar: "))
            if indice < 0 or indice >= len(registros):
                print("Índice inválido")
                return False
            
            registro_seleccionado = registros[indice]
            print(f"\nRegistro seleccionado: {registro_seleccionado}")
            
            # Mostrar campos disponibles
            print("\nCampos disponibles:", encabezados)
            
            # Seleccionar campo a modificar
            campo = input("Ingrese el campo a modificar: ")
            if campo not in encabezados:
                print("Campo inválido")
                return False
            
            # Nuevo valor
            nuevo_valor = input(f"Ingrese nuevo valor para '{campo}': ")
            
            # Confirmar
            print(f"\nCambio: {campo} = '{registro_seleccionado[campo]}' -> '{nuevo_valor}'")
            confirmacion = input("¿Confirmar modificación? (s/n): ")
            
            if confirmacion.lower() == 's':
                # Aplicar cambio
                registros[indice][campo] = nuevo_valor
                
                # Escribir de vuelta
                with open(archivo, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=encabezados)
                    writer.writeheader()
                    writer.writerows(registros)
                
                print("Registro modificado exitosamente")
                return True
            else:
                print("Modificación cancelada")
                return False
                
        except ValueError:
            print("Entrada inválida")
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False
    except Exception as e:
        print(f"Error al modificar registros: {e}")
        return False