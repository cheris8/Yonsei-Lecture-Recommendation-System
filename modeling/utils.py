def Preprocessor(data, text):
    
    import re
    from konlpy.tag import Mecab
    
    """ 불용어 리스트 불러오기 """
    with open('stopwordsFortopicmodeling.txt', 'r', encoding='utf-8') as f:
        stopwords = f.read().split('\n')
    
    """ 형태소 분석기 선언하기 """
    mecab = Mecab()
    
    """ 형태소 분석 수행하기 """
    docs = []
    tokens_cnt= []
    for t in text:
        t = re.sub('[\.!~A-z]+', '', str(t)) # 영어 및 특수문자 제거
        tokenized = mecab.morphs(t) # 형태소 분석
        words = []
        for token in tokenized:
            if (len(token)>1) and (token not in stopwords): # 길이가 1인 단어 제거, 불용어 제거
                words.append(token)
        docs.append(' '.join(words))
        tokens_cnt.append(len(words))
    
    """데이터셋에 형태소 분석 결과와 문서 당 토큰 개수 컬럼으로 추가하기"""
    data['TextPreprocessed'] = docs
    data['TokenCnt'] = tokens_cnt
    
    """형태소 분석 결과를 리스트로 저장하기"""
    docs_tokenized = data['TextPreprocessed'].apply(lambda x: x.split())
    
    return data, docs_tokenized
    
def ModelingLDA(text_tokenized, N=20):
    
    from gensim.corpora import Dictionary
    from gensim.models.ldamodel import LdaModel
    
    """단어 집합과 코퍼스 생성하기"""
    dictionary = Dictionary(text_tokenized)
    corpus = [dictionary.doc2bow(doc) for doc in text_tokenized]
    
    """LDA 수행하기"""
    lda = LdaModel(corpus, num_topics=N, id2word=dictionary, passes=50)
    
    """LDA 결과 출력하기"""
    topics = lda.print_topics(num_words=5)
    for topic in topics:
        print(topic)
    
    return corpus, lda

def MakeTopicTable(corpus, model):
    
    import pandas as pd
    
    """문서 별 가장 비중이 높은 토픽의 인덱스, 가장 비중이 높은 토픽의 비중, 토픽 리스트를 각각 컬럼으로 갖는 데이터셋 생성하기"""
    topic_table = pd.DataFrame()
    for i, topic_list in enumerate(model[corpus]):
        doc = topic_list[0] if model.per_word_topics else topic_list  
        doc = sorted(doc, key=lambda x: (x[1]), reverse=True)
        for j, (topic_idx, topic_prop) in enumerate(doc):
            if j==0:
                topic_table = topic_table.append(pd.Series([topic_idx, topic_prop, topic_list]), ignore_index=True)
            else:
                break
    topic_table.columns = ['TopicIndex', 'TopicProportion', 'TopicList'] # 컬럼명 변경
    topic_table['TopicIndex'] = topic_table['TopicIndex'].astype(int) # TopicIndex 컬럼 정수형으로 변경
    topic_table['TopicProportion'] = topic_table['TopicProportion'].apply(lambda x: round(x, 5)) # TopicProportion 컬럼 소수점 다섯번째자리까지 표현
    
    return topic_table