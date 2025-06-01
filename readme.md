# Chatbot with FastAPI

## Getting Started

1. Clone the repository

```bash
git clone https://github.com/PioneerSoft-sa/chatbot.git
```

2. Setup and activate a virtual environment

```bash
cd chatbot
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Setup vector store

```bash
python app/config/vector_store.py
```

5. Run the app

```bash
fastapi dev app/main.py
```

6. Access the app at http://localhost:8000