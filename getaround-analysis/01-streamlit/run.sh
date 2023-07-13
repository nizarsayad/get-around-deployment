docker run -it \
-v "$(pwd):/app" \
-p 8501:8501 \
-e PORT=8501 \
nizarsayad/streamlit