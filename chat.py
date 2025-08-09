import streamlit as st
from openai import OpenAI
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re

def get_openai_client(api_key):
    if not api_key:
        return None
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        test_response = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1
        )
        return client
    except Exception as e:
        st.error(f"Error with API key: {str(e)}")
        return None

def extract_text_from_pdf(pdf_file):
    try:
        if hasattr(pdf_file, 'read'):
            pdf_reader = PyPDF2.PdfReader(pdf_file)
        else:
            with open(pdf_file, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

def create_vector_database_from_uploaded_files(uploaded_files):
    if not uploaded_files:
        return None, None
    
    all_texts = []
    for uploaded_file in uploaded_files:
        st.info(f"Processing {uploaded_file.name}...")
        text = extract_text_from_pdf(uploaded_file)
        if text:
            all_texts.append(text)
    
    if not all_texts:
        st.error("No text extracted from uploaded PDFs")
        return None, None
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    chunks = []
    for text in all_texts:
        chunks.extend(text_splitter.split_text(text))
    
    if chunks:
        return None, chunks
    
    return None, None

def simple_keyword_search(prompt, chunks):
    prompt_words = set(re.findall(r'\b\w+\b', prompt.lower()))
    
    chunk_scores = []
    for i, chunk in enumerate(chunks):
        chunk_words = set(re.findall(r'\b\w+\b', chunk.lower()))
        score = len(prompt_words.intersection(chunk_words))
        chunk_scores.append((score, i, chunk))
    
    chunk_scores.sort(reverse=True)
    top_chunks = [chunk for score, i, chunk in chunk_scores[:3] if score > 0]
    
    return top_chunks

def get_rag_response(prompt, vector_db, chunks=None, client=None):
    if not client:
        return "Error: API client not available. Please enter a valid OpenRouter API key."
    
    try:
        if vector_db:
            relevant_docs = vector_db.similarity_search(prompt, k=3)
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
        elif chunks:
            relevant_chunks = simple_keyword_search(prompt, chunks)
            context = "\n\n".join(relevant_chunks) if relevant_chunks else ""
        else:
            context = ""

        if context:
            enhanced_prompt = f"""You are an experienced top tier management consultant and business advisor.
                                Use the following context from management documents to provide accurate, relevant advice.
                                Context from management documents:
                                {context}

                                User Question: {prompt}

                                Please provide a comprehensive answer based on the context provided,
                                and if the context doesn't fully address the question, supplement with your general management knowledge.
                                Always provide practical, actionable insights."""
        else:
            enhanced_prompt = f"""You are an experienced top tier management consultant and business advisor.
                                Provide professional, strategic advice on the following question:

                                User Question: {prompt}

                                Please provide practical, actionable insights with examples when appropriate."""
        
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=[
                {"role": "user", "content": enhanced_prompt}
            ],
            temperature=0.7,
            max_tokens=1500,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def get_deepseek_response(prompt, client=None):
    if not client:
        return "Error: API client not available. Please enter a valid OpenRouter API key."
    
    try:
        management_context = """You are an higly experienced top tier management consultant and business advisor. Provide professional, strategic advice on:
        - Leadership and team management
        - Business strategy and planning
        - Project management
        - Organizational development
        - Performance management
        - Change management
        - Decision making and problem solving
        - Communication and stakeholder management
        
        Always provide practical, actionable insights with examples when appropriate."""
        
        enhanced_prompt = f"{management_context}\n\nUser Question: {prompt}"
        
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=[
                {"role": "user", "content": enhanced_prompt}
            ],
            temperature=0.7,
            max_tokens=1500,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def streamlit_app():
    st.set_page_config(
        page_title="RAG Management Advisor",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 RAG Management Advisor")
    st.markdown("Your AI-powered business and management consultant with RAG capabilities")
    
    st.markdown("### 🔑 OpenRouter API Configuration")
    st.info("💡 This app uses the **deepseek/deepseek-chat-v3-0324:free** model from OpenRouter")
    
    # Initialize session state for API key management
    if "api_key_submitted" not in st.session_state:
        st.session_state.api_key_submitted = False
    if "stored_api_key" not in st.session_state:
        st.session_state.stored_api_key = ""
    if "client" not in st.session_state:
        st.session_state.client = None
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        api_key = st.text_input(
            "Enter your OpenRouter API Key:",
            type="password",
            placeholder="sk-or-v1-...",
            help="Get your free API key from https://openrouter.ai/ for the DeepSeek model",
            value=st.session_state.stored_api_key if st.session_state.api_key_submitted else ""
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        submit_clicked = st.button(
            "🔌 Connect",
            type="primary",
            disabled=not api_key,
            use_container_width=True
        )
    
    client = None
    if submit_clicked and api_key:
        with st.spinner("🔄 Connecting to OpenRouter API..."):
            client = get_openai_client(api_key)
            if client:
                st.session_state.api_key_submitted = True
                st.session_state.stored_api_key = api_key
                st.session_state.client = client
                st.success("✅ API Connected Successfully!")
                st.rerun()
    elif st.session_state.api_key_submitted and st.session_state.stored_api_key:
        client = st.session_state.client
        st.success("✅ API Connected")
        if st.button("🔄 Change API Key"):
            st.session_state.api_key_submitted = False
            st.session_state.stored_api_key = ""
            st.session_state.client = None
            st.rerun()
    elif api_key and not submit_clicked:
        st.warning("⚠️ Click 'Connect' to verify your API key")
    elif not api_key:
        st.warning("⚠️ API Key Required")
    
    st.markdown("---")
    
    st.markdown("### 📄 Document Upload (Optional)")
    uploaded_files = st.file_uploader(
        "Upload PDF documents for RAG-enhanced responses:",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload PDF files to enable document-based responses. Without uploads, you'll get a standard chatbot."
    )
    
    has_documents = False
    if uploaded_files:
        if "uploaded_file_names" not in st.session_state or st.session_state.uploaded_file_names != [f.name for f in uploaded_files]:
            with st.spinner("Processing uploaded documents..."):
                _, st.session_state.chunks = create_vector_database_from_uploaded_files(uploaded_files)
                st.session_state.uploaded_file_names = [f.name for f in uploaded_files]
                if st.session_state.chunks:
                    st.success(f"✅ Successfully processed {len(uploaded_files)} document(s)!")
                    has_documents = True
                else:
                    st.error("❌ Failed to process uploaded documents")
        else:
            if st.session_state.chunks:
                st.success(f"✅ Using {len(uploaded_files)} previously processed document(s)")
                has_documents = True
    else:
        if "chunks" in st.session_state:
            st.session_state.chunks = None
        if "uploaded_file_names" in st.session_state:
            st.session_state.uploaded_file_names = None
    
    if has_documents or (uploaded_files and st.session_state.get('chunks')):
        mode = "RAG Mode"
        st.info("🧠 **RAG Mode Active** - Using your uploaded documents for enhanced responses")
    else:
        mode = "Standard Mode"
        st.info("💬 **Standard Mode Active** - Upload PDF documents to enable RAG mode")
    
    st.markdown("---")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if not client:
        st.chat_input("Please enter a valid OpenRouter API key above to start chatting...", disabled=True)
    elif prompt := st.chat_input("Ask about management, leadership, business strategy, or questions about your uploaded documents..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Analyzing your management challenge..."):
                if mode == "RAG Mode" and st.session_state.get('chunks'):
                    response = get_rag_response(prompt, None, st.session_state.chunks, client)
                else:
                    response = get_deepseek_response(prompt, client)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    streamlit_app()