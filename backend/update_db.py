import sqlite3

def add_parroco_firmante():
    conn = sqlite3.connect(r'C:\Users\User\Documents\Datos Parroquia\parroquia.db')
    cursor = conn.cursor()
    
    tables = ['actas_bautizo', 'actas_matrimonio', 'actas_confirmacion', 'actas_comunion']
    
    for table in tables:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN parroco_firmante VARCHAR(255)")
            print(f"Added parroco_firmante to {table}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Column already exists in {table}")
            else:
                print(f"Error updating {table}: {e}")
                
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_parroco_firmante()
