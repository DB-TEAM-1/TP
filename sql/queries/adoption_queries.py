from django.db import connection

class AdoptionQueries:
    @staticmethod
    def get_user_adoptions(user_num):
        query = """
            SELECT A.adoption_id, A.status, A.applied_at,
                   I.kindNm, I.age, I.sexCd,
                   S.careNm, S.careAddr
            FROM Adoption A
            JOIN Animal I ON A.desertionNo = I.desertionNo
            JOIN Shelter S ON A.careRegNo = S.careRegNo
            WHERE A.user_num = %s
            ORDER BY A.applied_at DESC;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [user_num])
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def update_adoption_status(adoption_id, status):
        query = """
            UPDATE Adoption
            SET status = %s
            WHERE adoption_id = %s;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [status, adoption_id])
            return cursor.rowcount > 0 