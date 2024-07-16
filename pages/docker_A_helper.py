import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAI
from typing import List
from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser, CommaSeparatedListOutputParser, NumberedListOutputParser
from langchain_community.callbacks import get_openai_callback
import cohere
from langchain_core.documents import Document
from langchain.tools.tavily_search import TavilySearchResults


from langsmith import traceable


def retrieve_and_merge(query_list :list[str]) -> list[Document] :
    
    tavilysearch = TavilySearchResults(max_results= 3)
    result = []
    for query in query_list :
        result_temp = tavilysearch.invoke(query)
        result.extend(result_temp)
    #print(result)
        
    docs = {x['content']: i for i, x in enumerate(result)}
    rerank_input = list(docs.keys())
    #print(list(docs.keys()))
    
    return result, rerank_input

def rerank(rerank_input,question):
    #print(rerank_input.keys())
    
    co = cohere.Client()
    rerank_response = co.rerank(
        query=question, documents= rerank_input, top_n=5, model="rerank-multilingual-v3.0"
    )
    
    return rerank_response

def compress_retrieve(dict):
    
    search_results, rerank_input = retrieve_and_merge(dict['query_list'])
    rerank_response = rerank(rerank_input,dict['english_question'])
    docs = [search_results[i.index] for i in rerank_response.results]
    
    return docs

def format_docs(docs: List[Document]) -> str:
    #print(docs)
    #print(docs[0])
    formatted = [
        f"Source ID: {i+1}\nArticle Snippet: {doc['content']}"
        for i, doc in enumerate(docs)
    ]
    return "\n\n" + "\n\n".join(formatted)

@traceable
def generate_reponse():
    string_output_parser = StrOutputParser()
    
    number_output_parser = NumberedListOutputParser()
    number_format_instructions=number_output_parser.get_format_instructions()
    
    llm4o = ChatOpenAI(model="gpt-4o", temperature=0) 
    
    
    translator_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Translate the medical report in English. Also expand abbreviations.",
            ),
            ("human","{question}" ),
        ]
    )
    
    search_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a doctor residing in Korea. When given a medical related question, give a list of phrases you would search in order to retrieve information used to answer the question. Only give 3 or less phrases.\n{}".format(number_format_instructions),
            ),
            ("human","{english_question}" ),
        ]
    )
    
    response_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a Korean doctor. Answer the user question based on the given context and information given. DO NOT give diagnosis or direct advise. If a phrase is related with the context given. please add a tag of the source ID that looks like <|1|>. Use Korean : \n\n[Context]\n{context}""",
            ),
            ("human","{english_question}" ),
        ]
    )
    
    
    chain = (RunnableParallel(
        question = RunnablePassthrough(),
        english_question = translator_prompt| llm4o | string_output_parser,)
    .assign(query_list = search_prompt|llm4o|number_output_parser)
    .assign(docs={'query_list':itemgetter("query_list"),'english_question':itemgetter('english_question')}|RunnableLambda(compress_retrieve))
    .assign(context=itemgetter("docs") | RunnableLambda(format_docs))
    .assign(response=response_prompt |llm4o | string_output_parser )
    .pick(["response",'docs'])
    )

    
    return chain

def update_text():
    
    st.session_state.answer = st.session_state.temp_answer 


if 'answer' not in st.session_state:
    st.session_state.answer = ''

if 'question' not in st.session_state:
    st.session_state.question = "가족이 뇌혈관조영술 했는데 한쪽에 4mm정도되는 꽈리가 있어서 시술해야할 것 같다고합니다. 가장 빠른게 1년 뒤라고해서 일단 예약했는데 이게 원래 이렇게 늦게해도 되는 시술 인가요? 시술 빨리 되는 다른 병원으로 가야하나요?"
    
if 'additional_information' not in st.session_state:
    st.session_state.additional_information = """1. 60세 남성
2. 뇌혈관조영술 결과 외에 다른 증상이나 불편함 없음
3. 고혈압, 고지혈증 약 복용 중
4. 뇌동맥류 위치: 왼쪽, 크기: 4mm
5. 현재 예약된 병원의 시술 대기 시간이 긴 이유에 대해 설명을 듣지 못함"""
# if 'CC' not in st.session_state:
#     st.switch_page('app_streamlit.py')

st.session_state.question_full = st.session_state.question + '\n\n' +  st.session_state.additional_information

with st.form(key='response'):
    st.text_area('질문 및 추가정보', height=200, key='question_full')
    submitted = st.form_submit_button('질문 등록')
    if submitted :   
        chain = generate_reponse()
        st.session_state.temp_answer = chain.invoke({"question" : st.session_state.question})
        
    
        st.text_area('답변', value=st.session_state.temp_answer['response'], height=300, key='answer_text')
        st.text_area('링크', value='\n'.join([f"{i+1}. {entry['url']}\n{entry['content']}" for i, entry in enumerate(st.session_state.temp_answer['docs'])]), height=400, key='link_text')

st.button('답변 확정',on_click=update_text)
    
#print(st.session_state.messages)   
    