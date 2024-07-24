import os
import re
import streamlit as st
import time
from youtube_transcript_api import YouTubeTranscriptApi

from utils import youtube_code as yc

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

def main():
    st.title("유튜브 스크립트 불러오기")

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
            else:
                st.error("올바른 YouTube URL 형식이 아닙니다.")
        else:
            st.error("유효한 URL을 입력하세요.")

def main1():
    st.title('유튜브 스크립트 스크래핑')
    zero_code = '''
# YouTubeTranscriptApi를 사용하여 YouTube 영상의 자동 생성된 자막을 가져오는 함수
def get_transcript(video_id):
    try:
        # 해당 video_id의 영상에 대한 자막 목록을 가져옴
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        result = []
        # 각 자막에 대해 fetch를 수행하여 텍스트를 가져옴
        for transcript in transcript_list:
            for entry in transcript.fetch():
                result.append(entry["text"])

        # 모든 자막 텍스트를 하나의 문자열로 결합
        script = ' '.join(result)

        # 최종적으로 스크립트 반환
        return script
    except Exception as e:
        # 예외가 발생한 경우 Streamlit 앱에 에러 메시지 표시
        st.error(f"Error fetching transcript: {str(e)}")
'''
    yc.display_code(zero_code)

def main2():
    st.title('불러온 스크립트 요약하기')
    st.header('1. 스크립트 요약')
    first_code = ''' 
def summarize(input):
    # TokenTextSplitter를 사용하여 텍스트를 작은 청크로 분할
    text_splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=20)
    texts = text_splitter.split_text(input)
    
    # 텍스트를 Document 객체로 변환
    docs = [Document(page_content=t) for t in texts[:3]]
    
    # Summarization 모델과 연결된 Summarization 체인을 로드
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    
    # Summarization 체인을 사용하여 텍스트 요약 실행
    return chain.run(docs)

 '''
    yc.display_code(first_code)

def main3():
    st.header('2. 번역을 위한 chrome driver 셋팅')
    second_code = '''
# 번역을 위한 chrome driver 셋팅
def set_chrome_driver(headless=True):
    # Chrome 브라우저를 설정하기 위한 옵션 객체 생성
    options = webdriver.ChromeOptions()

    # headless가 True로 설정되어 있으면 브라우저를 숨겨 실행하는 옵션 추가
    if headless:
        options.add_argument('headless')

    # 브라우저의 User-Agent를 설정하는 옵션 추가
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36")

    # ChromeDriver를 사용하여 WebDriver 생성
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # 설정된 WebDriver 객체 반환
    return driver
'''
    yc.display_code(second_code)


def main4():
    st.header('3. 한글 스크립트 판단')
    third_code = '''
#한글과 영어가 혼동되어 요약하는 오류 해결을 위한 한글 스트립트 판단

# 한 글자가 한글인지 판단하는 함수
def is_korean(char):
    return '가' <= char <= '힣'

# 문자열에 한글이 포함되어 있는지 판단하는 함수
def contains_korean(text):
    return any('가' <= char <= '힣' for char in text)
'''
    yc.display_code(third_code)


def main5():
    st.header('4. 영어 스크립트인 경우 파파고로 번역')
    fourth_code = '''
# 주어진 텍스트가 한글을 포함하고 있지 않으면 Papago 번역기를 사용하여 해당 텍스트를 영어로 번역하는 함수
def papago_translate(text):
    # 만약 텍스트에 한글이 포함되어 있다면 번역을 하지 않고 원본 텍스트를 반환
    if contains_korean(text):
        return text
    else:
        try:
            # Chrome 드라이버를 설정하고 Papago 번역기 웹페이지에 접속
            papago = set_chrome_driver(True)
            papago.get('https://papago.naver.com/')
            time.sleep(1)

            # 번역할 텍스트를 Papago 번역기에 입력하고 번역 버튼 클릭
            papago.find_element(By.ID, 'txtSource').send_keys(text)
            papago.find_element(By.ID, 'btnTranslate').click()
            time.sleep(2)

            # 번역된 결과를 가져오기
            papago_translated = papago.find_element(By.ID, 'targetEditArea')
            result = papago_translated.text

        except NoSuchElementException:
            # 예외가 발생하면 '번역 오류ㅠㅠ' 메시지 반환
            result = '번역 오류ㅠㅠ'
        finally:
            # Chrome 창 닫기
            papago.close()

    return result
'''
    yc.display_code(fourth_code)

def main6():
    st.header('5. 요약 스크립트 토큰화')
    fifth_code = '''
# 한글 문장을 토큰화하는 함수
def tokenized(korean_sentence):
    # Okt(Okt 형태소 분석기) 객체 생성
    okt = Okt()
    
    # 토큰화된 데이터를 저장할 리스트 초기화
    tokenized_data = []
    
    # Okt를 사용하여 문장을 형태소로 분리 (stem=True는 각 단어의 원형을 사용하도록 함)
    tokenized_sentence = okt.morphs(korean_sentence, stem=True)
    
    # 불용어 제거
    stopwords_removed_sentence = [word for word in tokenized_sentence if not word in sw.stopwords]
    
    # 토큰화된 데이터 리스트에 추가
    tokenized_data.append(stopwords_removed_sentence)
    
    return tokenized_data
'''
    yc.display_code(fifth_code)

if __name__ == "__main__":
    main()
