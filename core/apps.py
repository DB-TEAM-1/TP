from django.apps import AppConfig
import os
from django.db import connection


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        try:
            with connection.cursor() as cursor:
                # Get the absolute path to the SQL directory
                sql_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sql')
                
                # Execute create_tables.sql first
                print("Creating tables...")
                with open(os.path.join(sql_dir, 'create_tables.sql'), 'r', encoding='utf-8') as f:
                    cursor.execute(f.read())
                    connection.commit()
                
                # Then execute insert files in order
                print("Inserting user data...")
                with open(os.path.join(sql_dir, 'inserts', 'user_inserts.sql'), 'r', encoding='utf-8') as f:
                    cursor.execute(f.read())
                    connection.commit()
                
                print("Inserting shelter data...")
                with open(os.path.join(sql_dir, 'inserts', 'shelter_inserts.sql'), 'r', encoding='utf-8') as f:
                    cursor.execute(f.read())
                    connection.commit()

                print("Inserting animal data...")
                with open(os.path.join(sql_dir, 'inserts', 'animal_inserts.sql'), 'r', encoding='utf-8') as f:
                    cursor.execute(f.read())
                    connection.commit()

                print("Inserting adoption data...")
                with open(os.path.join(sql_dir, 'inserts', 'adoption_inserts.sql'), 'r', encoding='utf-8') as f:
                    cursor.execute(f.read())
                    connection.commit()

                print("Inserting report data...")
                with open(os.path.join(sql_dir, 'inserts', 'report_inserts.sql'), 'r', encoding='utf-8') as f:
                    cursor.execute(f.read())
                    connection.commit()

                print("Database initialization completed successfully!")

        except Exception as e:
            print(f"Error initializing database: {e}")
            print("SQL directory:", sql_dir)
            print("Current working directory:", os.getcwd())