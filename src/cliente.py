# SISTEMA INTEGRAL DE GESTION - SOFTWARE FJ
# PROGRAMACIÓN - (213023A_2204)
# director de curso Fabian Augusto Avila Orjuela
#estudiantes:Leidy Paola Peralta Fuquene, Maria Paula Perez Rodriguez, Enmanuel Alejandro Corredor Mesa, Cristian Andres Martinez,Geidy Lorena Perez Villanueva


#clase cliente
class Cliente:

    def __init__(self, identificacion, nombre, correo, telefono):
        self.__identificacion = identificacion
        self.__nombre = nombre
        self.__correo = correo
        self.__telefono = telefono

        # guardar datos limpios
        if isinstance(self.__identificacion, str):
            self.__identificacion = self.__identificacion.strip()
        if isinstance(self.__nombre, str):
            self.__nombre = self.__nombre.strip()
        if isinstance(self.__correo, str):
            self.__correo = self.__correo.strip()
        if isinstance(self.__telefono, str):
            self.__telefono = self.__telefono.strip()

        self.valido = self.validar_datos()

    # validar datos
    def validar_datos(self):

        # validar identificacion
        if not isinstance(self.__identificacion, str) or not self.__identificacion.strip():
            print("La identificacion es obligatoria")
            correcto = False

        # validar nombre
        if not isinstance(self.__nombre, str) or not self.__nombre.strip():
            print("el nombre es obligatorio")
        elif not self.__nombre.replace(" ", "").isalpha():
            print("el nombre solo debe contener letras")
            correcto = False

        # validar correo
        if not isinstance(self.__correo, str):
            print("el correo debe ser texto")
            correcto = False
        else:
            correo = self.__correo.strip()
            if "@" not in correo or "." not in correo.split("@")[-1]:
                print("el correo electronico no es valido")
                correcto = False

        # validar telefono
        if not isinstance(self.__telefono, str):
            print("el telefono debe ser texto")
            correcto = False
        else:
            telefono = self.__telefono.strip()
            if not telefono.isdigit() or len(telefono) != 10:
                print("el telefono debe tener exactamente 10 numeros")
                correcto = False

    # consultar informacion
    def obtener_identificacion(self):
        return self.__identificacion

    def obtener_nombre(self):
        return self.__nombre

    def obtener_correo(self):
        return self.__correo

    def obtener_telefono(self):
        return self.__telefono

    # mostrar informacion de cliente
    def mostrar_datos(self):
        print("\nDATOS DEL CLIENTE")
        print("identificacion:", self.__identificacion)
        print("nombre:", self.__nombre)
        print("correo:", self.__correo)
        print("telefono:", self.__telefono)
class Main:

    def iniciar(self):
        print("\nREGISTRO DE CLIENTES")

        identificacion = input("ingrese la identificacion: ")
        nombre = input("ingrese el nombre: ")
        correo = input("ingrese el correo electronico: ")
        telefono = input("ingrese el telefono: ")

        # crear objeto de la clase Cliente
        cliente = Cliente(identificacion, nombre, correo, telefono)

        #comprobar si los datos son correctos
        if cliente.valido:
            print("\ncliente registrado correctamente")
            cliente.mostrar_datos()
        else:
            print("\nno se pudo registrar el cliente. Revise los datos.")

if __name__ == "__main__":
    programa = Main()
    programa.iniciar()
