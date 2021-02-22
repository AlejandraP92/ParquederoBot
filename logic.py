from sqlalchemy.sql.elements import Null
from sqlalchemy.sql.expression import null
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import DateTime
import database.db as db
import sqlite3
from datetime import datetime
from sqlalchemy import extract
from models.Administrador import Administrador
from models.Vehiculo import Vehiculo
from models.Zona import Zona
from models.Tiquete import Tiquete

#########################################################
def insert_admins():
    #admin1 = Administrador(1528370599)#Marco Montoya
    #admin2 = Administrador(1221493315)#Alejandra Peralta
    #admin3 = Administrador(1551638159)#Jose Omar Cardona
    #admin4 = Administrador(1563918474)#Cristian Ruiz
    administradores = [1528370599,1221493315,1551638159,1563918474]
    for index in administradores:
        admin = None
        admin = db.session.query(Administrador).get(index)

        if admin == None:
            admin = Administrador(index)
            db.session.add(admin)
            db.session.commit()
#########################################################
def get_about_this(VERSION):
    response = (
    f"Parqueadero UAM Bot (pyTelegramBot) v{VERSION}"
    "\n\n"
    "Desarrollado por:"
    "\n\n"
    "Alejandra Peralta <alejandra.peraltad@autonoma.edu.co>"
    "\n\n"
    "Marco Montoya <marcoa.montoyam@autonoma.edu.co>"
    "\n\n"
    "Jose Omar Cardona <joseo.cardonag@autonoma.edu.co>"
    "\n\n"
    "Cristian Ruiz <cristian.ruizvm@autonoma.edu.co>"
    )
    return response

#########################################################
def get_welcome_message(bot_data):
    response = (
    f"🤖 Hola, soy *{bot_data.first_name}* "
    f"también conocido como *{bot_data.username}*.\n\n"
    "¡Estoy aquí para ayudarte en todo lo relacionado con los parqueaderos de la UAM!"
    )
    return response

#########################################################
def get_help_message ():
    response = (
    "Estos son los comandos y órdenes disponibles:\n"
    "\n"
    "*/start* - Inicia la interacción con el bot (obligatorio)\n"
    "*/help* - Muestra este mensaje de ayuda\n"
    "*/about* - Muestra detalles de esta aplicación\n"
    "*agregar zona|agz {idzona}, {disponible}* - Agregar Nueva Zona (sólo admin)\n"
    "*listar zonas|lsz* - Listar Zonas Agregadas (sólo admin)\n"
    "*remover zona|rmz {idzona}* - Remover Zona (sólo admin)\n"
    "*agregar vehiculo|agv placa {placa} , tipo {tipo}* (Tipos Vehículo: 1. Carro, 2. Moto)- Agregar Vehículo\n"
    "*listar vehiculos|lsv* - Listar Vehículos\n"
    "*remover vehiculo|rmv placa {placa}* - Remover Vehiculo\n"
    "*registrar ingreso|ingreso|ring {placa} en la zona {idzona}* - Registrar Ingreso Vehículo\n"
    "*registrar salida|salida|rsal {placa}* - Registrar Salida Vehículo\n"
    "*ubicar vehiculo|ubicar|ubv {placa}* - Ubicar Vehículo\n"
    )
    return response
#########################################################
#Obtener Zona
def get_zona (placa_vehiculo):
    id_ve=db.session.query(Vehiculo).filter_by(placa=placa_vehiculo).get(id_vehiculo)
    
    zona=db.session.query(Tiquete).filter_by(id_vehiculo=id_ve).get(id_zona)

    db.session.commit()

    return zona

#########################################################
#Agregar Vehículo
def add_vehiculo(tipoVehiculo, placa, idUsuario):  
    
    nuevoVehiculo = Vehiculo(idUsuario, tipoVehiculo, placa)

    if not nuevoVehiculo:
        db.session.rollback()
        return False  

    db.session.add(nuevoVehiculo)
    db.session.commit()

    return True

######################################################### 
# Listar Vehículo
def list_vehiculos():
	vehiculo = db.session.query(Vehiculo).all()

	return vehiculo

######################################################### 
# Eliminar Vehículo
def remove_vehiculo(user_id, placaVehiculo):
    vehiculo = db.session.query(Vehiculo).filter(
        Vehiculo.id_usuario == user_id
    ).filter(
        Vehiculo.placa == placaVehiculo
    ).first()

    if not vehiculo:
        db.session.rollback()
        return False   

    db.session.delete(vehiculo)    
    db.session.commit()
    
    return True        

######################################################### 
# Registrar Ingreso del Vehiculo
def ingresar_vehiculo(user_id, placaVehiculo, zonaVehiculo):

    duracion = float(0); 

    vehiculo = db.session.query(Vehiculo).filter(
        Vehiculo.id_usuario == user_id
    ).filter(
        Vehiculo.placa == placaVehiculo
    ).first()

    idVehiculo = vehiculo.id_vehiculo

    nuevoIngreso = Tiquete(idVehiculo, zonaVehiculo, duracion)

    if not nuevoIngreso:
        db.session.rollback()
        return False  

    db.session.add(nuevoIngreso)
    db.session.commit()

    return True

######################################################### 
# Registrar Salidad del Vehiculo 
def reg_salida_vehiculo(user_id, placaVehiculo):   

    vehiculo = db.session.query(Vehiculo).filter(
        Vehiculo.id_usuario == user_id
    ).filter(
        Vehiculo.placa == placaVehiculo
    ).first()

    idVehiculo = int(vehiculo.id_vehiculo)

    db.engine.execute("UPDATE tiquete SET fecha_salida = datetime('now') WHERE duracion = 0 and id_vehiculo = {};".format(idVehiculo))    

    db.session.commit()

    calcularDuaracion(idVehiculo)    
    
    db.session.close()
    
    return True   

#########################################################  
# Consultar la disponibilidad de la zona 
def get_disponibilidad_zona(zonaVehiculo):    

    zona = db.session.query(Zona).filter(
        Zona.id_zona == zonaVehiculo
    ).first()

    disponibilidad = zona.disponible

    if disponibilidad == 1 : 
        return True
    if disponibilidad == 0 : 
        return False

#########################################################
# Actualizar la disponibilidad de la zona 
def update_dispo_zona(zonaVehiculo, estado):    

    zona = db.session.query(Zona).filter(
        Zona.id_zona == zonaVehiculo
    ).first()

    zona.disponible =+ estado
    
    db.session.commit()

    return True   
#########################################################
# Calcular y actualizar la duracion en el parqueadero
def calcularDuaracion(idVehiculo):    

    db.engine.execute("UPDATE tiquete SET duracion = (Select Cast (( JulianDay(fecha_salida) - JulianDay(fecha_ingreso)) * 24 As Integer) dur from tiquete WHERE duracion = 0 and id_vehiculo = {0}) WHERE duracion = 0 and id_vehiculo = {0};".format(idVehiculo))  

    db.session.commit()

    return True     

#########################################################
def get_fallback_message (text):
    response = f"\U0001F648 No entendí lo que me acabas de decir"  
    return response

#########################################################