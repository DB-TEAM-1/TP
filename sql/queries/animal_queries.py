from django.db import connection

class AnimalQueries:
    @staticmethod
    def get_animal(desertionNo):
        query = """
            SELECT *
            FROM "Animal"
            WHERE desertionNo = %s;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [desertionNo])
            columns = [desc[0] for desc in cursor.description]
            row = cursor.fetchone()
            if row:
                return dict(zip(columns, row))
            return None

    @staticmethod
    def search_animals(upKindCd=None, sexCd=None, age=None, happenPlace=None, processState=None):
        query = """
            SELECT * FROM Animal
            WHERE 1=1
        """
        values = []

        if upKindCd:
            query += " AND upKindCd = %s"
            values.append(upKindCd)
        
        if sexCd:
            query += " AND sexCd = %s"
            values.append(sexCd)
        
        if age:
            query += " AND age LIKE %s"
            values.append(f'%{age}%')
        
        if happenPlace:
            query += " AND happenPlace LIKE %s"
            values.append(f'%{happenPlace}%')
        
        if processState:
            query += " AND processState = %s"
            values.append(processState)

        with connection.cursor() as cursor:
            cursor.execute(query, values)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def search_female_dogs_in_seoul():
        query = """
            SELECT * FROM Animal
            WHERE upKindCd = '417000'
            AND sexCd = 'F'
            AND age LIKE '%2023%'
            AND happenPlace LIKE '%서울%'
            AND processState = '보호중';
        """
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def get_animal_detail(desertionNo):
        query = """
            SELECT * FROM Animal
            WHERE desertionNo = %s;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [desertionNo])
            columns = [desc[0] for desc in cursor.description]
            row = cursor.fetchone()
            if row:
                return dict(zip(columns, row))
            return None

    @staticmethod
    def get_shelter_by_animal(desertionNo):
        query = """
            SELECT s.* FROM Shelter s
            WHERE careRegNo = (
                SELECT careRegNo FROM Animal
                WHERE desertionNo = %s
            );
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [desertionNo])
            columns = [desc[0] for desc in cursor.description]
            row = cursor.fetchone()
            if row:
                return dict(zip(columns, row))
            return None

    @staticmethod
    def update_animal(desertionNo, **kwargs):
        updates = []
        values = []
        
        for field, value in kwargs.items():
            updates.append(f"{field} = %s")
            values.append(value)
        
        if not updates:
            return False
            
        query = f"""
            UPDATE Animal
            SET {', '.join(updates)}
            WHERE desertionNo = %s;
        """
        values.append(desertionNo)
        
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            return cursor.rowcount > 0 