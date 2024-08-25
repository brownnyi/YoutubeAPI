import os
import re
import streamlit as st
import time
import stopwords as sw
from youtube_transcript_api import YouTubeTranscriptApi
from langchain import OpenAI
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import TokenTextSplitter
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from konlpy.tag import Okt

# OpenAI API key
os.environ["OPENAI_API_KEY"] = "XXXX"

# Initialize OpenAI language model
llm = OpenAI(temperature=0)

# 유튜브 스크립트 스크래핑
def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        result = []
        for transcript in transcript_list:
            for entry in transcript.fetch():
                result.append(entry["text"])

        script = ' '.join(result)

        return script
    except Exception as e:
        st.error(f"Error fetching transcript: {str(e)}")

# 스크립트 요약
def summarize(input):
    text_splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=20)
    texts = text_splitter.split_text(input)
    docs = [Document(page_content=t) for t in texts[:3]]
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    return chain.run(docs)

# 번역을 위한 chrome driver 셋팅
def set_chrome_driver(headless=True):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('headless')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# summarize시 한글과 영어가 혼동되어 요약되는 오류 해결위해서 한글스크립트 판단
def is_korean(char):
    return '가' <= char <= '힣'

def contains_korean(text):
    return any('가' <= char <= '힣' for char in text)

# 영어요약스크립트시 파파고로 번역
def papago_translate(text):
    if contains_korean(text):
        return text
    else:
        try:
            papago = set_chrome_driver(True)
            papago.get('https://papago.naver.com/')
            time.sleep(1)
            papago.find_element(By.ID, 'txtSource').send_keys(text)
            papago.find_element(By.ID, 'btnTranslate').click()
            time.sleep(2)
            papago_translated = papago.find_element(By.ID, 'targetEditArea')
            result = papago_translated.text
        except NoSuchElementException:
            result = '번역 오류ㅠㅠ'
        finally:
            papago.close()

    return result

# 요약 스크립트 토큰화
def tokenized(korean_sentecne):
    okt = Okt()
    tokenized_data = []
    tokenized_sentence = okt.morphs(korean_sentecne, stem=True)
    stopwords_removed_sentence = [word for word in tokenized_sentence if not word in sw.stopwords]
    tokenized_data.append(stopwords_removed_sentence)
    return tokenized_data

# streamlit으로 앱 노출
def main():
    st.title("YouTube 요약 앱")

    url = st.text_input("URL을 입력하세요:", value="")
    go_button = st.button("시작!")

    if go_button:
        if url:
            match = re.search("v=(.*)", url)
            if match:
                with st.spinner('트랜스크립트를 가져오는 중...'):
                    url_id = match.group(1)
                    script = get_transcript(url_id)
                st.subheader("전체 스크립트:")
                st.text_area(label="전체 스크립트", value=script, height=400)
                with st.spinner('요약 중...'):
                    sum_res = summarize(script)
                    if is_korean(sum_res[0]):  # 가정: 요약 결과의 첫 번째 문장으로 언어를 판단
                        trans_res = sum_res
                    else:
                        trans_res = papago_translate(sum_res)
                st.subheader("요약 결과:")
                st.write(trans_res)
                with st.spinner('토큰화 작업 중...'):
                    tk = tokenized(trans_res)
                st.subheader("토큰화 결과:")
                st.write(tk)
            else:
                st.error("올바른 YouTube URL 형식이 아닙니다.")
        else:
            st.error("유효한 URL을 입력하세요.")

if __name__ == "__main__":
    main()
