from flask import Flask, request, jsonify
import numpy as np
import requests
from PIL import Image
from io import BytesIO
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import mysql.connector

app = Flask(__name__)

# VGG16 모델 로드
base_model = VGG16(weights='imagenet')
model = Model(inputs=base_model.input, outputs=base_model.get_layer('fc1').output)

def get_db_connection():
    """MySQL 데이터베이스에 연결을 설정합니다."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="< MySQL password >",
        database="my_db"
    )

def load_features(filename='webtoon_features.pkl'):
    """저장된 특징 벡터를 로드합니다."""
    with open(filename, 'rb') as f:
        return pickle.load(f)

# 특징 벡터 로드
webtoon_features = load_features()

def load_webtoon_titles_and_urls():
    """데이터베이스에서 웹툰 제목과 URL을 로드합니다."""
    conn = get_db_connection()
    query = "SELECT title, thumbnail_link FROM webtoons"
    df = pd.read_sql(query, conn)
    conn.close()
    return dict(zip(df['title'], df['thumbnail_link']))

webtoon_title_to_url = load_webtoon_titles_and_urls()

def download_and_preprocess_image(url):
    """이미지를 다운로드하고 전처리합니다."""
    headers = {'Referer': 'https://m.comic.naver.com/index'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        img = img.convert('RGB')
        img = img.resize((224, 224))
        img_data = image.img_to_array(img)
        img_data = np.expand_dims(img_data, axis=0)
        img_data = preprocess_input(img_data)
        return img_data
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return None

def extract_features(img_data):
    """이미지의 특징 벡터를 추출합니다."""
    features = model.predict(img_data)
    return features.flatten()

def recommend_similar_webtoons(input_title, top_n=20):
    """입력된 웹툰 제목과 유사한 웹툰을 추천합니다."""
    input_image_url = webtoon_title_to_url.get(input_title)
    if not input_image_url:
        return []

    input_img_data = download_and_preprocess_image(input_image_url)
    if input_img_data is None:
        return []

    input_features = extract_features(input_img_data)
    similarities = {}
    for url, data in webtoon_features.items():
        features = data['features']
        similarity = cosine_similarity([input_features], [features])[0][0]
        similarities[url] = {'similarity': similarity, 'title': data['title']}
    
    sorted_similarities = sorted(similarities.items(), key=lambda item: item[1]['similarity'], reverse=True)
    
    # 추천 결과 생성
    recommended_results = [{
        'title': data[1]['title'],
        'similarity': data[1]['similarity'],
        'image_url': url
    } for url, data in sorted_similarities[:top_n]]
    
    return recommended_results

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    """웹툰 제목을 입력받아 유사한 웹툰을 추천합니다."""
    data = request.json
    input_title = data.get('title')
    if not input_title:
        return jsonify({"error": "웹툰 제목을 입력해 주세요."}), 400

    recommendations = recommend_similar_webtoons(input_title)
    
    return jsonify(recommendations)

if __name__ == "__main__":
    app.run(port = 5000)
