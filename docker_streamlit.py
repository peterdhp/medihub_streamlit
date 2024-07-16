import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAI
from langchain_core.output_parsers import StrOutputParser, NumberedListOutputParser, CommaSeparatedListOutputParser
from langchain_community.callbacks import get_openai_callback
from menu_streamlit import menu_with_redirect
from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)
import os
from langsmith import traceable



if "messages" not in st.session_state:
    st.session_state.messages = []
    
if 'add_question' not in st.session_state:
    st.session_state.add_question = ['']
    
if 'question' not in st.session_state:
    st.session_state.question = ''
    

def LLM_respond_Q(msg_log):
    """채팅 내용을 기반으로 질문을 함"""

    system_prompt = [("system", """You are a Korean doctor. you are going to ask the patient additional questions needed to retrieve information to answer his/her initial question. Ask one question at a time. 
ALL the questions in the list MUST be asked. 
HOWEVER, when the patient information doesn't match the content of the question, skip the question. For example, don't ask appenditis related question for patient with appendectomy history.
If there are no questions in the question list. Assume no additional questions are needed. 
If there are no more questions to be asked, please output <|endofQuestion|>. Do not answer the initial question.:
    
    [initial question]
    {question}
    
    [question list]
    {question_list}                   
    """)]
    
    prompt_temp = system_prompt + msg_log
    
    prompt = ChatPromptTemplate.from_messages(prompt_temp)
    
    llm = ChatOpenAI(model_name="gpt-4o", temperature = 0) 
    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser    
    
    output = chain.stream({"question" : st.session_state.question, "question_list": "\n ".join(st.session_state.add_question)})
    return output

def LLM_Summary(msg_log):
    """채팅 내용을 기반으로 질문을 함"""

    system_prompt = [("system", """You are a Korean doctor. you are going to ask the patient additional questions needed to retrieve information to answer his/her initial question. Ask one question at a time. 
ALL the questions in the list MUST be asked. 
HOWEVER, when the patient information doesn't match the content of the question, skip the question. For example, don't ask appenditis related question for patient with appendectomy history.
If there are no questions in the question list. Assume no additional questions are needed. 
If there are no more questions to be asked, please output <|endofQuestion|>. Do not answer the initial question.
When asked to summarize, please summarize what the patient said in the chat. Give the output in Korean and a list, only output the list.:
    
    [initial question]
    {question}
    
    [question list]
    {question_list}                   
    """),
                    ]  

    prompt_temp = system_prompt + msg_log + [("user", "summarize")]
               
    
    
    
    prompt = ChatPromptTemplate.from_messages(prompt_temp)
    
    llm = ChatOpenAI(model_name="gpt-4o", temperature = 0) 
    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser    
    
    output = chain.stream({"question": st.session_state.question, "question_list": "\n ".join(st.session_state.add_question)})
    return output
    
def question_generator(model):
    number_output_parser = NumberedListOutputParser()
    format_instructions=number_output_parser.get_format_instructions()
    prompt_addQ = ChatPromptTemplate.from_messages([
        ("system", "You are a Korean doctor consulting a patient. When given a medical complaint, ask questions that would help you answer the question. The maximum number of questions should be 5. If no question need to be asked, output empty list. \n{}".format(format_instructions)),
        ("user", "\n{question}")
    ])

    prompt_verify = ChatPromptTemplate.from_messages([
        ("system", "Verify whether a question is a medical related question or not. Simply, output T if it's medical related and F if it isn't. no need to explain"),
        ("user", "\n{question}")
    ])

    llm4o = ChatOpenAI(model_name=model, temperature = 0)





    chain_addQ = prompt_addQ | llm4o | number_output_parser
    chain_verify = prompt_verify | llm4o | StrOutputParser()

    chain = RunnableParallel(
        addQ = chain_addQ,
        verify = chain_verify
    ) 
    return chain
    
    
def demo():
    st.session_state.status = "chat"
    st.session_state.messages = []
    
def refresh():
    st.session_state.messages =[]
    st.rerun()
    
    
@st.experimental_dialog("죄송합니다.")
def throw_error(verify_result):
    if verify_result == "F":
        st.write("닥터플렉스는 건강 및 의학 관련된 질문만 받을 수 있습니다")
        if st.button("다시 질문하기") :
            st.session_state.messages = []
            st.rerun()
    if verify_result == "T":
        st.rerun()

for message in st.session_state.messages:
    role = '🩺' if message[0] == 'ai' else message[0]
    with st.chat_message(role):
        st.markdown(message[1])
        
        
        
if len(st.session_state.messages) ==0 : 
    #print(st.session_state.add_question)
    st.session_state.messages.append(('ai','안녕하세요? 닥터플렉스입니다. 건강상 간단한 질문에 대해서 의사선생님이 답변을 드립니다.' ))
    st.session_state.messages.append(('ai','어떤게 궁금하신가요? 자세한 질문일수록 의사 선생님께서 더 잘 답변 드릴 수 있습니다.' ))
    
    with st.chat_message("🩺"):
        st.markdown('안녕하세요?  닥터플렉스 입니다. 건강상 간단한 질문에 대해서 의사선생님이 답변을 드립니다.')
    with st.chat_message("🩺"):
        st.markdown('어떤게 궁금하신가요? 자세한 질문일수록 의사 선생님께서 더 잘 답변 드릴 수 있습니다.' )

        
if userinput := st.chat_input("메시지를 입력해주세요."):
    # Add user message to chat history
    st.session_state.messages.append(("human", userinput))
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(userinput)
        
        
    if len(st.session_state.messages) == 3 :
        st.session_state.question  = userinput
        response = question_generator('gpt-4o').invoke(st.session_state.question)
        st.session_state.add_question = response['addQ']
        if response['verify'] == "F":
            throw_error(response['verify'])
            st.stop()
            
    
    # Display assistant response in chat message container
    with st.chat_message("🩺"):
        stream = LLM_respond_Q(st.session_state.messages)
        response = st.write_stream(stream)
        if response.strip() != '<|endofQuestion|>' :
            st.session_state.messages.append(("ai", response))
    
        else :
            summary = LLM_Summary(st.session_state.messages)
            st.write('답변해주셔서 감사합니다. 환자분께서 말씀해주신 것을 요약해보겠습니다.')
            st.session_state.additional_information = st.write_stream(summary)
            st.write('해당 내용이 맞다면 등록하기 버튼을 눌러주세요.')

            st.session_state.messages.append(('ai','답변해주셔서 감사합니다. 환자분께서 말씀해주신 것을 요약해보겠습니다.\n\n'+st.session_state.additional_information + '\n\n해당 내용이 맞다면 등록하기 버튼을 눌러주세요.'))
            st.page_link("pages/docker_A_helper.py",label="등록하기")
            
            # if st.button("등록하기") :
            #     st.info("질문이 등록되었습니다.", icon="✅")
            #     st.switch_page("docker_A_helper.py")
    
    
