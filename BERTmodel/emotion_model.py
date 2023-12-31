import tensorflow as tf
import numpy as np
from konlpy.tag import Kkma
from keras.models import load_model
from transformers import DistilBertTokenizer, TFDistilBertForSequenceClassification

kkma = Kkma()
model_name = "distilbert-base-multilingual-cased"
model = TFDistilBertForSequenceClassification.from_pretrained(
    model_name,
    num_labels=5
)
tokenizer = DistilBertTokenizer.from_pretrained(model_name)

class EmotionAnalysis :
    def __init__(self) :
        self.model = model
        self.model.load_weights('BERTmodel/model.h5/tf_model.h5')
    
    # 바트모델에 적합하게 문장 전처리
    def BERTtokenizer(self, data):
        input_ids = tokenizer(data,
                              truncation = True,
                              padding = True)
        input_ids = tf.data.Dataset.from_tensor_slices((dict(input_ids),)).batch(32)
        return input_ids
        
    # 각 문장별로 어떤 감정을 내포하고 있는지 분류하고 summarize_emotion 리스트를 반환
    def prob_emotion(self, input_sentence) :
        input_ids = self.BERTtokenizer(input_sentence)
        
        summarize_emotion = []
        emotion_lst = ["기쁨", "당황", "분노", "불안", "슬픔"]
        prediction = self.model.predict(input_ids, verbose=1)
        for sent, emotion in zip(input_sentence, prediction["logits"]) :
            logits = np.array(emotion)
            softmax_scores = np.exp(logits) / np.sum(np.exp(logits))
            dominant_emotion = np.argmax(softmax_scores) 
            summarize_emotion.append([sent, emotion_lst[dominant_emotion], format(softmax_scores[dominant_emotion]*100,".2f")])
            
        return summarize_emotion
    
    def print_emotion(self, sentence) :
        for text in sentence :
            print(f'"{text[0]}"은 {text[2]}%의 확률로 {text[1]}을 나타내는 문장입니다.')
            
    def result_emotion(self, sentence) :
        dic_emotion = {"기쁨" : 0, "당황" : 0, "분노" : 0, "불안" : 0, "슬픔" : 0}
        dic_count = {"기쁨" : 0, "당황" : 0, "분노" : 0, "불안" : 0, "슬픔" : 0}
        dic_ratio = {"기쁨" : 0, "당황" : 0, "분노" : 0, "불안" : 0, "슬픔" : 0}
        sum_sent = 0
        score = 0
        
        for text in sentence :
            dic_emotion[text[1]] += float(text[2])
            dic_count[text[1]] += 1
            sum_sent += 1
            
        if sum_sent != 0 :
            for e in dic_emotion :
                if dic_count[e] != 0 :
                    dic_ratio[e] = round((dic_count[e] / sum_sent) * 100, 3)
                    
        for e in dic_emotion :
            if dic_count[e] != 0 :
                dic_emotion[e] = dic_emotion[e] / dic_count[e]
            if e == "기쁨" :
                score += dic_emotion[e] * (dic_ratio[e] / 100)
            else :
                score -= dic_emotion[e] * (dic_ratio[e] / 100)
        score = (score + 100) / 2
        score = round(score, 3)
        
        return score, dic_ratio
            
    # 주어진 전체 문장을 kkma 객체를 이용하여 문장별로 분류
    def analyze_emotion(self, input_sentence) :
        sentence = kkma.sentences(input_sentence)
        sentence = self.prob_emotion(sentence)
        emotion_score, emotion_ratio = self.result_emotion(sentence)
        
        return emotion_score, emotion_ratio