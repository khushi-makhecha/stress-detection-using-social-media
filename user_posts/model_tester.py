import joblib
from transformers import BertTokenizer, BertModel  # If using BERT

lr_classifier = joblib.load('user_posts/models/lr_model.joblib')
tfidf_vectorizer = joblib.load('user_posts/models/tfidf_vectorizer.joblib')  # If using TF-IDF

def predict_stress_level(text):
    '''Function to preprocess and predict the stress level of a given text'''
    try:
        features = tfidf_vectorizer.transform([text])
        prediction = lr_classifier.predict(features)

        return prediction[0]
    except Exception as e:
        print(f'An exception occurred in predict_stress_level: {str(e)}')
        return 0