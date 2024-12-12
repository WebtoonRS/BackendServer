# StyleBasedRS.py는 거의 동일하지만 image_embedding을 사용
import sys
import json
import mysql.connector
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sookmyung2024",
        database="webtoon_db",
        auth_plugin='mysql_native_password'
    )

def get_recommendations(user_data):
    try:
        webtoon_id = user_data.get('webtoon_id')
        if not webtoon_id:
            raise ValueError("webtoon_id is required")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 모든 웹툰의 정보와 이미지 임베딩 가져오기
        cursor.execute("""
            SELECT id, title, thumbnail_link as Thumb, synopsis, image_embedding 
            FROM webtoons
        """)
        results = cursor.fetchall()

        # 임베딩 데이터 처리
        embeddings = []
        webtoons_data = []
        for row in results:
            embedding = np.frombuffer(row['image_embedding'], dtype=np.float32)
            embeddings.append(embedding)
            webtoons_data.append(row)
        
        embeddings = np.array(embeddings)

        # 나머지 로직은 StoryBasedRS.py와 동일
        selected_idx = next(i for i, w in enumerate(webtoons_data) if w['id'] == int(webtoon_id))
        selected_embedding = embeddings[selected_idx].reshape(1, -1)
        cosine_similarities = cosine_similarity(selected_embedding, embeddings).flatten()
        
        similar_indices = np.argsort(cosine_similarities)[::-1]
        similar_indices = similar_indices[similar_indices != selected_idx][:9]
        
        recommendations = {
            "recommendations": [
                {
                    "id": webtoons_data[idx]['id'],
                    "title": webtoons_data[idx]['title'],
                    "thumbnail_link": webtoons_data[idx]['Thumb'],
                    "synopsis": webtoons_data[idx]['synopsis'],
                    "similarity_score": float(cosine_similarities[idx])
                } for idx in similar_indices
            ]
        }
        
        cursor.close()
        conn.close()
        
        print(json.dumps(recommendations))
        
    except Exception as e:
        error_response = {"error": str(e)}
        print(json.dumps(error_response))

if __name__ == "__main__":
    try:
        user_data = json.loads(sys.argv[1])
        get_recommendations(user_data)
    except Exception as e:
        print(json.dumps({"error": f"Failed to parse input: {str(e)}"}))