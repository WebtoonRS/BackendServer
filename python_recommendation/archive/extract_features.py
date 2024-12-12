import pandas as pd
import numpy as np
import requests
from PIL import Image
from io import BytesIO
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model
import pickle

# VGG16 모델 설정
base_model = VGG16(weights='imagenet')
model = Model(inputs=base_model.input, outputs=base_model.get_layer('fc1').output)

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

def main():
    # CSV 파일 로드
    df = pd.read_csv('webtoon_data_embeddings.csv', encoding='utf-8')
    
    # 이미지 특징 추출
    image_features = {}
    for idx, row in df.iterrows():
        print(f"Processing {row['title']}...")
        img_data = download_and_preprocess_image(row['Thumb'])
        if img_data is not None:
            features = extract_features(img_data)
            image_features[idx] = features
    
    # 특징 벡터 저장
    with open('webtoon_image_features.pkl', 'wb') as f:
        pickle.dump(image_features, f)
    
    print("Feature extraction completed!")

if __name__ == "__main__":
    main() 