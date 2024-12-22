import streamlit as st
 
st.set_page_config(
    page_title="PP RAG POC",
    layout="wide",
)
 
st.title(":star: PP")
st.write('---')
st.markdown("### Chat :speech_balloon:")
st.markdown("* [LLM] sr-llm-65b-instruct")
st.markdown("* [I2T] llama-3-2-90b-vision-instruct")
st.write('---')
st.markdown("### RAG :mag_right:")
st.markdown("* [Embedding] sds-embed")
st.markdown("* [Rerank] sds-rerank")
st.write('---')
st.markdown("### Generative ✨")
st.markdown("* [T2I] flux-1-schnell-diffusion")
st.write('---')
st.markdown("### Repo :file_folder:")
st.markdown("* [VectorDB] Elastic Search")
st.write('---')
st.write("created by 40465 황태경")
st.write('v24.12.19.')