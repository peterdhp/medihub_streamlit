import streamlit as st
from menu_streamlit import menu
from utils_streamlit import *

from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.output_parsers.openai_tools import JsonOutputKeyToolsParser
from typing import List
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser, CommaSeparatedListOutputParser, NumberedListOutputParser
from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
    RunnableAssign
)
import os

from langsmith import traceable


os.environ["LANGCHAIN_API_KEY"]=st.secrets['LANGCHAIN_API_KEY']
os.environ["LANGCHAIN_TRACING_V2"]=st.secrets['LANGCHAIN_TRACING_V2']
os.environ["LANGCHAIN_ENDPOINT"]=st.secrets['LANGCHAIN_ENDPOINT']
os.environ['LANGCHAIN_PROJECT']=st.secrets['LANGCHAIN_PROJECT']
os.environ['OPENAI_API_KEY']=st.secrets['OPENAI_API_KEY']
os.environ['CO_API_KEY']=st.secrets['CO_API_KEY']



# Initialize st.session_state.role to None
if "status" not in st.session_state:
    st.session_state.status = None
    
if "demo" not in st.session_state:
    st.session_state.demo = None
    
if "role" not in st.session_state:
    st.session_state.role = 'patient'
    
if "question" not in st.session_state:
    st.session_state.question = ''
    
if "add_question" not in st.session_state:
    st.session_state.add_question = []


def demo():
    # Callback function to save the role selection to Session State
    st.session_state.status = "text"
    st.session_state._question="""가족이 뇌혈관조영술 했는데 한쪽에 4mm정도되는 꽈리가 있어서 시술해야할 것 같다고합니다. 가장 빠른게 1년 뒤라고해서 일단 예약했는데 이게 원래 이렇게 늦게해도 되는 시술 인가요? 시술 빨리 되는 다른 병원으로 가야하나요?"""
    st.session_state.question=st.session_state._question
    st.session_state.add_question = [ "가족분의 나이와 성별은 어떻게 되시나요?","뇌혈관조영술 결과 외에 다른 증상이나 불편함이 있으신가요?" ,"가족분의 과거 병력이나 현재 복용 중인 약물이 있나요?", "뇌동맥류의 위치와 크기에 대해 더 자세히 설명해 주실 수 있나요?", "현재 예약된 병원의 시술 대기 시간이 긴 이유에 대해 설명을 들으셨나요?"]

    


@st.cache(allow_output_mutation=True)
    
@traceable
def question_generator(model):
    comma_output_parser = CommaSeparatedListOutputParser()
    number_output_parser = NumberedListOutputParser()
    format_instructions=number_output_parser.get_format_instructions()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Korean doctor consulting a patient. When given a medical complaint, ask questions that would help you answer the question. The maximum number of questions should be 5. If no question need to be asked, output empty list. \n{}".format(format_instructions)),
        ("user", "\n{question}")
    ])

    llm = ChatOpenAI(model_name=model, temperature = 0)  #gpt-4-turbo-preview #gpt-3.5-turbo #gpt-4 #gpt-3.5-turbo-1106

    chain = prompt | llm | number_output_parser    
    return chain


def submit():
    st.session_state.status = "text"
    st.session_state.question=st.session_state._question
    st.session_state.add_question = question_generator('gpt-4o').invoke(st.session_state.question)
    


st.title("질문 입력")

with st.form(key='demographics_form'):
    
    st.text_area('어떤 것이 궁금하신가요? 의사가 직접 답변드립니다.', placeholder='가능한 자세히 작성하실수록 더 정확한 답변을 드릴 수 있습니다.',key='_question', height=200)
    
    if st.form_submit_button("등록하기",on_click = submit):
        print(st.session_state.add_question)
        st.switch_page('pages/Q_helper_chat_stopToken.py')
        

    

with st.sidebar:
     st.button("DEMO : 질문등록 ",on_click=demo)
menu() # Render the dynamic menu!




