from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import pickle

app = Flask(__name__)
CORS(app)

# CSV 파일 로드
df = pd.read_csv('webtoon_data_embeddings.csv', encoding='utf-8')

# text_embedding 컬럼의 문자열을 numpy 배열로 변환
df['text_embedding'] = df['text_embedding'].apply(lambda x: np.fromstring(
    x.strip('[]'), sep=','))

# 텍스트 임베딩 벡터를 numpy 배열로 변환
text_embeddings = np.stack(df['text_embedding'].values)

# 저장된 이미지 특징 벡터 로드
def load_image_features(filename='webtoon_image_features.pkl'):
    """저장된 이미지 특징 벡터를 로드합니다."""
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        print(f"Error loading image features: {e}")
        return None

# 이미지 특징 벡터 로드
image_features = load_image_features()

@app.route('/api/webtoons/style_recommendations', methods=['POST'])
def style_recommendations():
    try:
        data = request.get_json()
        title = data.get('title')
        print(f"Received request for style recommendations - Title: {title}")

        # 입력된 제목으로 웹툰 찾기
        webtoon = df[df['title'] == title]
        if webtoon.empty:
            return jsonify({"error": "Webtoon not found"}), 404

        # 입력 웹툰의 인덱스 찾기
        input_idx = webtoon.index[0]
        
        if input_idx not in image_features:
            return jsonify({"error": "Image features not found"}), 404

        input_features = image_features[input_idx]
        
        # 유사도 계산
        similarities = []
        for idx, features in image_features.items():
            if idx != input_idx:  # 입력 웹툰 제외
                similarity = cosine_similarity([input_features], [features])[0][0]
                similarities.append((idx, similarity))
        
        # 유사도 기준으로 정렬
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # 상위 9개 추천
        recommendations = []
        for idx, similarity in similarities[:9]:
            recommendations.append({
                "id": int(idx),
                "title": df.iloc[idx]['title'],
                "thumbnail_link": df.iloc[idx]['Thumb'],
                "synopsis": df.iloc[idx]['synopsis'],
                "similarity_score": float(similarity)
            })

        return jsonify(recommendations)

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/webtoons/story_recommendations', methods=['POST'])
def story_recommendations():
    try:
        data = request.get_json()
        title = data.get('title')
        print(f"Received request for story recommendations - Title: {title}")

        # 입력된 제목으로 웹툰 찾기
        webtoon = df[df['title'] == title]
        if webtoon.empty:
            return jsonify({"error": "Webtoon not found"}), 404

        # 텍스트 임베딩 기반 추천
        selected_idx = webtoon.index[0]
        selected_embedding = text_embeddings[selected_idx].reshape(1, -1)
        similarities = cosine_similarity(selected_embedding, text_embeddings).flatten()
        
        similar_indices = np.argsort(similarities)[::-1]
        similar_indices = similar_indices[similar_indices != selected_idx][:9]
        
        recommendations = [
            {
                "id": int(df.iloc[idx].name),  # index를 id로 사용
                "title": df.iloc[idx]['title'],
                "thumbnail_link": df.iloc[idx]['Thumb'],
                "synopsis": df.iloc[idx]['synopsis'],
                "similarity_score": float(similarities[idx])
            } for idx in similar_indices
        ]

        return jsonify(recommendations)

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/webtoons/multiple_story_recommendations', methods=['POST'])
def multiple_story_recommendations():
    try:
        data = request.get_json()
        titles = data.get('titles', [])
        print(f"Received request for multiple story recommendations - Titles: {titles}")

        if not titles:
            return jsonify({"error": "No titles provided"}), 400

        # 입력된 제목들로 웹툰 찾기
        selected_webtoons = df[df['title'].isin(titles)]
        if selected_webtoons.empty:
            return jsonify({"error": "No webtoons found"}), 404

        # 선택된 웹툰들의 임베딩 평균 계산
        selected_indices = selected_webtoons.index
        selected_embeddings = text_embeddings[selected_indices]
        average_embedding = np.mean(selected_embeddings, axis=0).reshape(1, -1)

        # 코사인 유사도 계산
        similarities = cosine_similarity(average_embedding, text_embeddings).flatten()
        
        # 선택된 웹툰들을 제외하고 상위 20개 추천
        similar_indices = np.argsort(similarities)[::-1]
        similar_indices = similar_indices[~np.isin(similar_indices, selected_indices)][:20]
        
        recommendations = [
            {
                "id": int(df.iloc[idx].name),
                "title": df.iloc[idx]['title'],
                "thumbnail_link": df.iloc[idx]['Thumb']
            } for idx in similar_indices
        ]

        return jsonify(recommendations)

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True) 