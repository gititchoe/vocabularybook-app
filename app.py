import streamlit as st
import pandas as pd
import random

# CSV 파일 불러오기
try:
    df = pd.read_csv('toeic_words.csv')
    df = df.fillna('')  # NaN 값을 빈 문자열로 채우기
except FileNotFoundError:
    st.error("`toeic_words.csv` 파일을 찾을 수 없습니다.")
    st.stop()

# 세션 상태(session_state)에 저장할 변수 초기화
if 'random_words' not in st.session_state:
    st.session_state.random_words = df.sample(4)
if 'expanded_card_index' not in st.session_state:
    st.session_state.expanded_card_index = -1
if 'starred_words_indices' not in st.session_state:
    st.session_state.starred_words_indices = []
# 퀴즈 관련 상태 초기화
if 'quiz_state' not in st.session_state:
    st.session_state.quiz_state = {'question_word': None, 'options': [], 'correct_answer': '', 'is_answered': False, 'score': 0}
if 'quiz_history' not in st.session_state:
    st.session_state.quiz_history = []
if 'quiz_correct_count' not in st.session_state:
    st.session_state.quiz_correct_count = 0
if 'quiz_total_count' not in st.session_state:
    st.session_state.quiz_total_count = 0

# 단어 카드를 위한 함수
def create_card(word_data, index, column):
    with column:
        with st.container(border=True):
            col_text, col_star = st.columns([0.8, 0.2])
            is_starred = index in st.session_state.starred_words_indices
            star_icon = "⭐" if is_starred else "☆"

            with col_text:
                st.markdown(f"<h2 style='margin-bottom: 5px;'>{word_data['단어']}</h2><p style='margin: 0;'>{word_data['뜻']}</p>", unsafe_allow_html=True)
            
            with col_star:
                if st.button(star_icon, key=f"star_btn_{index}"):
                    if is_starred:
                        st.session_state.starred_words_indices.remove(index)
                    else:
                        st.session_state.starred_words_indices.append(index)
                    st.rerun()

            st.markdown("<hr style='margin-top: 0; margin-bottom: 5px; border-top: 1px solid #ddd;'>", unsafe_allow_html=True)

            if st.button('▼', use_container_width=True, key=f'expand_btn_{index}'):
                if st.session_state.expanded_card_index == index:
                    st.session_state.expanded_card_index = -1
                else:
                    st.session_state.expanded_card_index = index
            
            if st.session_state.expanded_card_index == index:
                st.write("---")
                st.markdown(f"**예문:** {word_data['예문']}", unsafe_allow_html=True)
                st.markdown(f"**유의어:** {word_data['유의어']}", unsafe_allow_html=True)

# 퀴즈 문제 생성 함수
def generate_quiz():
    st.session_state.quiz_total_count += 1
    
    # 정답 단어 무작위 선택
    correct_word_data = df.sample(1).iloc[0]
    correct_answer = correct_word_data['뜻']
    
    # 오답 3개 무작위 선택
    incorrect_options = df[df['뜻'] != correct_answer].sample(3)['뜻'].tolist()
    
    options = incorrect_options + [correct_answer]
    random.shuffle(options)
    
    st.session_state.quiz_state['question_word'] = correct_word_data['단어']
    st.session_state.quiz_state['options'] = options
    st.session_state.quiz_state['correct_answer'] = correct_answer
    st.session_state.quiz_state['is_answered'] = False

#==================================================
# 사이드바 메뉴와 페이지 구성
#==================================================

with st.sidebar:
    st.header("메뉴")
    menu_selection = st.radio("이동", ["오늘의 단어", "별표 단어장", "전체 단어장", "퀴즈"])

if menu_selection == "오늘의 단어":
    st.title('나만의 영어 단어장')
    
    if st.button('단어 새로고침', key='refresh_btn'):
        st.session_state.random_words = df.sample(4)
        st.session_state.expanded_card_index = -1

    st.subheader('오늘의 단어 4개')

    col1, col2 = st.columns(2)
    for i in range(4):
        original_index = st.session_state.random_words.iloc[i].name
        if i % 2 == 0:
            create_card(st.session_state.random_words.iloc[i], original_index, col1)
        else:
            create_card(st.session_state.random_words.iloc[i], original_index, col2)

elif menu_selection == "별표 단어장":
    st.title("별표 단어장")
    
    starred_indices = st.session_state.starred_words_indices
    if starred_indices:
        starred_words_df = df.loc[starred_indices]
        
        st.subheader(f"총 {len(starred_words_df)}개의 단어")
        
        col1, col2 = st.columns(2)
        for i, (index, row) in enumerate(starred_words_df.iterrows()):
            if i % 2 == 0:
                create_card(row, index, col1)
            else:
                create_card(row, index, col2)
    else:
        st.info("아직 별표 표시한 단어가 없습니다.")

elif menu_selection == "전체 단어장":
    st.title("전체 단어장")

    st.subheader(f"총 {len(df)}개의 단어")
    
    col1, col2 = st.columns(2)
    for i, (index, row) in enumerate(df.iterrows()):
        if i % 2 == 0:
            create_card(row, index, col1)
        else:
            create_card(row, index, col2)

elif menu_selection == "퀴즈":
    st.title("퀴즈")

    # 퀴즈 상태가 초기화되지 않았으면 문제 생성
    if not st.session_state.quiz_state['question_word']:
        generate_quiz()

    st.subheader(f"문제 {st.session_state.quiz_total_count}")
    st.write(f"### **{st.session_state.quiz_state['question_word']}**")

    # 객관식 보기 버튼
    for option in st.session_state.quiz_state['options']:
        if st.button(option, key=option, use_container_width=True):
            if not st.session_state.quiz_state['is_answered']:
                st.session_state.quiz_state['is_answered'] = True
                if option == st.session_state.quiz_state['correct_answer']:
                    st.success("정답입니다! 🎉")
                    st.session_state.quiz_correct_count += 1
                else:
                    st.error(f"오답입니다. 정답은 '{st.session_state.quiz_state['correct_answer']}'입니다.")
    
    st.write(f"현재 점수: {st.session_state.quiz_correct_count} / {st.session_state.quiz_total_count}")

    if st.session_state.quiz_state['is_answered']:
        if st.button('다음 문제'):
            generate_quiz()
            st.rerun()