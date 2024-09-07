import pandas as pd
import numpy as np
import mysql.connector

# CSV 데이터 로드
df = pd.read_csv('C:/Users/82105/Webtoon_project/python_recommendation/combined_webtoon_data.csv')

# 임베딩 데이터 로드
embeddings = np.load('C:/Users/82105/Webtoon_project/python_recommendation/embeddings.npy')

# 데이터베이스 연결 설정
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="< MySQL password >",
    database="my_db"
)
cursor = conn.cursor()

# 데이터베이스에 데이터 삽입
for i, row in df.iterrows():
    embedding_blob = embeddings[i].astype(np.float32).tobytes()  # 임베딩을 BLOB 형식으로 변환
    cursor.execute(
        "INSERT INTO webtoons (title, author, star_score, genre, keywords, synopsis, thumbnail_link, content, embedding) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (row['title'], row['author'], row['star_score'], row['genre'], row['keywords'], row['synopsis'], row['Thumb'], row['content'], embedding_blob)
    )

    #쿼리 작성

# 커밋 및 연결 종료
conn.commit()
cursor.close()
conn.close()
