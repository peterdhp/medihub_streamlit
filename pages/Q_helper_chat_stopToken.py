import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks import get_openai_callback
from menu_streamlit import menu_with_redirect



if "messages" not in st.session_state:
    st.session_state.messages = []
    
if st.session_state.add_question == []  :
    st.session_state.add_question = ['']
    
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

    prompt_temp = system_prompt + msg_log + ("user", "summarize")
               
    
    
    
    prompt = ChatPromptTemplate.from_messages(prompt_temp)
    
    llm = ChatOpenAI(model_name="gpt-4o", temperature = 0) 
    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser    
    
    output = chain.stream({"question": st.session_state.question, "question_list": "\n ".join(st.session_state.add_question)})
    return output
    
    
    
    
def demo():
    st.session_state.status = "chat"
    st.session_state.messages = []


for message in st.session_state.messages:
    role = '🩺' if message[0] == 'ai' else message[0]
    with st.chat_message(role):
        st.markdown(message[1])
        
        
        
if len(st.session_state.messages) ==0 : 
    print(st.session_state.add_question)
    st.session_state.messages.append(('ai','의사 선생님께서 더 자세하고 답변을 하실 수 있도록 몇가지 추가로 여쭙겠습니다.\n\n'+st.session_state.add_question[0]))
    
    with st.chat_message("🩺"):
        st.markdown('의사 선생님께서 더 자세하고 답변을 하실 수 있도록 몇가지 추가로 여쭙겠습니다.\n\n'+st.session_state.add_question[0])

        
if userinput := st.chat_input("답변을 적어주세요"):
    # Add user message to chat history
    st.session_state.messages.append(("human", userinput))
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(userinput)
        
        
        
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
            st.page_link("pages/A_helper.py", label="등록하기")
    
    


with st.sidebar:
    st.button("Demo",on_click=demo)
menu_with_redirect()
