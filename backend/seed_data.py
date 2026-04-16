import sys
import os
from datetime import datetime, timedelta
import random

# Add backend to path
sys.path.append(os.getcwd())
from app.db.session import SessionLocal
from app.models import all_models as models

db = SessionLocal()

def seed_bautizos(n=300):
    print(f"Insertando {n} bautizos...")
    nombres = ["Juan", "Maria", "Pedro", "Ana", "Sebastian", "Sofia", "Luis", "Elena", "Andres", "Isabel"]
    apellidos = ["Perez", "Garcia", "Lopez", "Martinez", "Rodriguez", "Hernandez", "Gomez", "Sanchez", "Navarro", "Díaz"]
    
    for i in range(n):
        nombre = random.choice(nombres)
        apellido = f"{random.choice(apellidos)} {random.choice(apellidos)}"
        fecha = datetime.now() - timedelta(days=random.randint(1, 3650))
        acta = models.ActaBautizo(
            nombre=nombre,
            apellidos=apellido,
            fecha_nacimiento=fecha.date() - timedelta(days=random.randint(30, 200)),
            lugar_nacimiento="Magangué",
            fecha_bautizo=fecha.date(),
            nombre_padre=f"{random.choice(nombres)} {random.choice(apellidos)}",
            nombre_madre=f"{random.choice(nombres)} {random.choice(apellidos)}",
            nombre_padrino=f"{random.choice(nombres)} {random.choice(apellidos)}",
            nombre_madrina=f"{random.choice(nombres)} {random.choice(apellidos)}",
            nombre_cura="Pbro. Edison",
            da_fe="Pbro. Juan",
            libro=str(random.randint(1, 20)),
            folio=str(random.randint(1, 400)),
            numero=str(random.randint(1, 1000))
        )
        db.add(acta)
    db.commit()

def seed_matrimonios(n=200):
    print(f"Insertando {n} matrimonios...")
    nombres = ["Sebastian", "Mayda", "Juan", "Sofia", "Pedro", "Elena", "Luis", "Isis", "Carlos", "Diana"]
    apellidos = ["Benitez", "Escorcia", "Navarro", "Herrera", "Gomez", "Díaz", "Lopez", "Martinez"]
    
    for i in range(n):
        fecha = datetime.now() - timedelta(days=random.randint(1, 3650))
        acta = models.ActaMatrimonio(
            nombre_esposo=random.choice(nombres),
            apellidos_esposo=f"{random.choice(apellidos)} {random.choice(apellidos)}",
            nombre_esposa=random.choice(nombres),
            apellidos_esposa=f"{random.choice(apellidos)} {random.choice(apellidos)}",
            fecha_matrimonio=fecha.date(),
            nombre_padrino=f"{random.choice(nombres)} {random.choice(apellidos)}",
            nombre_madrina=f"{random.choice(nombres)} {random.choice(apellidos)}",
            nombre_testigo1=f"{random.choice(nombres)} {random.choice(apellidos)}",
            nombre_testigo2=f"{random.choice(nombres)} {random.choice(apellidos)}",
            nombre_cura="Pbro. Juan",
            da_fe="Pbro. Juan",
            libro=str(random.randint(1, 15)),
            folio=str(random.randint(1, 300)),
            numero=str(random.randint(1, 800))
        )
        db.add(acta)
    db.commit()

def seed_aportes(n=50):
    print(f"Insertando {n} aportes...")
    tipos = ["Diezmo", "Ofrenda", "Donación Especial", "Venta Templo"]
    
    for i in range(n):
        fecha = datetime.now() - timedelta(days=random.randint(1, 365))
        aporte = models.Aporte(
            monto=random.choice([10000, 20000, 50000, 100000, 200000, 500000]),
            fecha=fecha.date(),
            tipo=random.choice(tipos),
            id_persona=None
        )
        db.add(aporte)
    db.commit()

if __name__ == "__main__":
    try:
        seed_bautizos(300)
        seed_matrimonios(200)
        seed_aportes(50)
        print("Carga de datos completada con éxito.")
    except Exception as e:
        print(f"Error durante la carga: {e}")
    finally:
        db.close()
