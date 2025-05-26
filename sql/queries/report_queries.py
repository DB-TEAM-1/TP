from django.db import connection

class ReportQueries:
    @staticmethod
    def get_user_reports(user_num):
        query = """
            SELECT * FROM Report
            WHERE user_num = %s
            ORDER BY reported_dt DESC;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [user_num])
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()] 