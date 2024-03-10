import joblib
from transformers import BertTokenizer, BertModel  
import torch


# Load the SVM classifier (ensure the path is correct)
svm_classifier = joblib.load('user_posts/models/svm_model.joblib')

# Initialize the BERT tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')


def preprocess_text_with_bert(text):
    '''Function to preprocess text using BERT to extract features'''
    try:
        tokens = tokenizer(text, padding=True, truncation=True, max_length=512, return_tensors='pt')
        with torch.no_grad():
            outputs = model(**tokens)
        return outputs.last_hidden_state[:, 0, :].numpy()  
    except Exception as e:
        print(f'An exception occurred in preprocess_text_with_bert: {str(e)}')
        return None


def predict_stress_level(text):
    '''Function to preprocess and predict the stress level of a given text using SVM and BERT'''
    try:
        features = preprocess_text_with_bert(text)
        prediction = svm_classifier.predict(features)

        return prediction[0]
    except Exception as e:
        print(f'An exception occurred in predict_stress_level: {str(e)}')
        return 0