from django.db import connection

class ShelterQueries:
    @staticmethod
    def get_shelter(careRegNo):
        query = """
            SELECT *
            FROM Shelter
            WHERE careRegNo = %s;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [careRegNo])
            columns = [desc[0] for desc in cursor.description]
            row = cursor.fetchone()
            if row:
                return dict(zip(columns, row))
            return None

    @staticmethod
    def search_shelters(region=None, limit=None, offset=None):
        query = "SELECT * FROM Shelter WHERE 1=1"
        values = []

        if region:
            query += " AND (careAddr LIKE %s OR jibunAddr LIKE %s)"
            values.extend([f'%{region}%', f'%{region}%'])

        if limit:
            query += " LIMIT %s"
            values.append(limit)

        if offset:
            query += " OFFSET %s"
            values.append(offset)

        with connection.cursor() as cursor:
            cursor.execute(query, values)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def update_shelter(careRegNo, **kwargs):
        updates = []
        values = []
        
        for field, value in kwargs.items():
            updates.append(f"{field} = %s")
            values.append(value)
        
        if not updates:
            return False
            
        query = f"""
            UPDATE Shelter
            SET {', '.join(updates)}
            WHERE careRegNo = %s;
        """
        values.append(careRegNo)
        
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            return cursor.rowcount > 0 