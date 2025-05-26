from django.db import connection

class ReviewQueries:
    @staticmethod
    def get_shelter_reviews(careRegNo):
        query = """
            SELECT R.review_id, R.rating, R.comment, R.created_at,
                   U.name, A.kindNm, A.age, S.careNm, S.careAddr
            FROM Review R
            JOIN User U ON R.user_num = U.user_num
            JOIN Animal A ON R.desertionNo = A.desertionNo
            JOIN Shelter S ON R.careRegNo = S.careRegNo
            ORDER BY R.created_at DESC;
        """
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def update_review(review_id, rating=None, comment=None, image_url=None):
        updates = []
        values = []
        
        if rating is not None:
            updates.append("rating = %s")
            values.append(rating)
        if comment is not None:
            updates.append("comment = %s")
            values.append(comment)
        if image_url is not None:
            updates.append("image_url = %s")
            values.append(image_url)
        
        if not updates:
            return False
            
        query = f"""
            UPDATE Review
            SET {', '.join(updates)}
            WHERE review_id = %s;
        """
        values.append(review_id)
        
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            return cursor.rowcount > 0

    @staticmethod
    def delete_review(review_id):
        query = """
            DELETE FROM Review
            WHERE review_id = %s;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [review_id])
            return cursor.rowcount > 0 