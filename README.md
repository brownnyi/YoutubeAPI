가짜뉴스 탐지 프로젝트 당시 만들었던 유튜브 API를 활용하여 유튜브 영상에 대한 스크립트를 텍스트 형태로 바꾸는 코드
![image](https://github.com/user-attachments/assets/434fb2d4-0d5f-4289-8f52-547d5633031b)

- Streamlit 활용 코드로 웹페이지로 사용 가능한 형태
- openai api가 결제해서 사용해야하는 방식이라 많이 사용시에 트래픽 초과
- 데이터 분석시 의미가 없는 단어(stopwords)때문에 전처리 과정이 복잡해져 이를 제거하기 위해 stopwords.py를 stopwords에 대한 전처리 과정을 거친다.
