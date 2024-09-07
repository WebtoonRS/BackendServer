from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import mysql.connector
import random

app = Flask(__name__)

def get_db_connection():
    """MySQL 데이터베이스에 연결을 설정합니다."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="< MySQL password >",
        database="my_db"
    )

# 자동완성 기능 구현
@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    term = request.args.get('term', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT title FROM webtoons WHERE title LIKE %s LIMIT 10"
    cursor.execute(query, ('%' + term + '%',))
    
    results = cursor.fetchall()
    suggestions = [row[0] for row in results]
    
    cursor.close()
    conn.close()
    
    return jsonify(suggestions)

# 데이터 로드 기능 수정
def load_data_recommendation(genre=None):
    """MySQL 데이터베이스에서 장르에 따라 데이터를 로드하고 전처리합니다."""
    conn = get_db_connection()
    query = "SELECT id, title, genre, thumbnail_link FROM webtoons"
    if genre and genre.lower() != 'all':
        query += " WHERE genre LIKE %s"
        df = pd.read_sql(query, conn, params=(f'%{genre}%',))
    else:
        df = pd.read_sql(query, conn)
    conn.close()
    return df

def load_embeddings(df):
    """MySQL 데이터베이스에서 임베딩 데이터를 로드합니다."""
    conn = get_db_connection()
    ids = df['id'].tolist()
    format_strings = ','.join(['%s'] * len(ids))
    cursor = conn.cursor()
    cursor.execute(f"SELECT embedding FROM webtoons WHERE id IN ({format_strings})", tuple(ids))
    embeddings = cursor.fetchall()
    embeddings = [np.frombuffer(embedding[0], dtype=np.float32) for embedding in embeddings]
    conn.close()
    return np.vstack(embeddings)

def recommend_webtoons(df, embeddings, selected_indices):
    """코사인 유사도를 기반으로 선택된 웹툰에 대한 추천을 생성합니다."""
    all_recommendations = pd.DataFrame()
    for index in selected_indices:
        selected_embedding = embeddings[index].reshape(1, -1)  # selected_indices는 0부터 시작하는 인덱스입니다.
        cosine_similarities = cosine_similarity(selected_embedding, embeddings).flatten()

        recommendations_df = pd.DataFrame({
            'recommended_for': df.iloc[index]['title'],  
            'title': df['title'],
            'thumbnail_link': df['thumbnail_link'],
            'similarity_score': cosine_similarities
        })

        # 선택된 웹툰과 자기 자신을 제외하고, 중복된 제목 제거
        recommendations_df = recommendations_df.sort_values(by='similarity_score', ascending=False)
        recommendations_df = recommendations_df[recommendations_df.index != index]  # 자기 자신을 제외
        recommendations_df = recommendations_df.drop_duplicates(subset='title')  # 중복된 제목 제거
        recommendations_df = recommendations_df.head(3)
        
        all_recommendations = pd.concat([all_recommendations, recommendations_df])

    return all_recommendations

#무작위로 장르에 따른 웹툰 30개 보내주는 api
@app.route('/get_webtoons', methods=['POST'])
def get_webtoons():
    genre = request.json.get('genre')

    conn = get_db_connection()
    query = "SELECT title, thumbnail_link FROM webtoons WHERE genre LIKE %s"
    cursor = conn.cursor()
    cursor.execute(query, ('%' + genre + '%',))
    results = cursor.fetchall()

    # 무작위로 30개의 웹툰을 선택.
    selected_webtoons = random.sample(results, min(30, len(results)))

    cursor.close()
    conn.close()

    return jsonify(selected_webtoons)

#넘겨진 웹툰에 따른 추천 결과를 넘김
@app.route('/recommend', methods=['POST'])
def get_recommendations():
    genre = request.json.get('genre')
    selected_indices = request.json['selected_indices']
    
    df_filtered = load_data_recommendation(genre)  # 선택된 장르에 맞는 웹툰을 로드
    embeddings_filtered = load_embeddings(df_filtered)  # 필터링된 임베딩 로드
    
    # 추천 생성
    recommendations = recommend_webtoons(df_filtered, embeddings_filtered, selected_indices)
    return jsonify(recommendations.to_dict(orient='records'))



if __name__ == "__main__":
    app.run(debug=True)


## 웹툰을 랜덤하게 보내주고, 안드로이드에서 선택된 웹툰들에 대해서 저장해서 장르-웹툰 형식으로 한번에 전송