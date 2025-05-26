from django.db import connection
from django.contrib.auth.hashers import make_password

class UserQueries:
    @staticmethod
    def create_user(username, password, name, region=None, email=None):
        query = """
            INSERT INTO "User" (username, password, name, region, email, is_active, date_joined)
            VALUES (%s, %s, %s, %s, %s, true, CURRENT_TIMESTAMP)
            RETURNING user_num;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [username, make_password(password), name, region, email])
            return cursor.fetchone()[0]

    @staticmethod
    def get_user_by_username(username):
        query = """
            SELECT user_num, username, password, name, region, email, is_active
            FROM "User"
            WHERE username = %s;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [username])
            row = cursor.fetchone()
            if row:
                return {
                    'user_num': row[0],
                    'username': row[1],
                    'password': row[2],
                    'name': row[3],
                    'region': row[4],
                    'email': row[5],
                    'is_active': row[6]
                }
            return None

    @staticmethod
    def update_user(user_num, **kwargs):
        allowed_fields = ['name', 'region', 'email', 'password']
        updates = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                if field == 'password':
                    value = make_password(value)
                updates.append(f"{field} = %s")
                values.append(value)
        
        if not updates:
            return False
            
        query = f"""
            UPDATE "User"
            SET {', '.join(updates)}
            WHERE user_num = %s
            RETURNING user_num;
        """
        values.append(user_num)
        
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            return cursor.fetchone() is not None

    @staticmethod
    def delete_user(user_num):
        query = """
            DELETE FROM "User"
            WHERE user_num = %s
            RETURNING user_num;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [user_num])
            return cursor.fetchone() is not None 