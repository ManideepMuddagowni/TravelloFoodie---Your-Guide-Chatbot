## 🌟 TravelloFoodie - Your Guide AI Chatbot 🌟
---
### Overview
#### Developed a Generative AI-powered travel chatbot for my travel website for retrieving and presenting website information using web scraping and conversational AI for dynamic and interactive user experiences
---
### This solution is built using completely open-source technologies
---
#### 🛠️ Core Functionality
- 🌐 Website Scraping: Extracts internal links and content from a specified website.
- 🤖 Conversational AI: Provides intelligent, context-aware responses to user queries.
- 🔄 Context Maintenance: Ensures seamless and accurate conversation flow.

#### 💻 Technologies Used
- LangChain 🧠: Enables conversational logic and retrieval-based query answering.
- Chroma 📂: Supports vector-based document storage and retrieval.
- FastAPI 🚀: Back-end API framework for managing requests efficiently.
- Frontend 🎨: Built using HTML, CSS, and JavaScript for a smooth user interface.
- ChatGroq ⚡: Incorporates Llama-3.1 for advanced AI-driven conversations.
---

### Demo

https://github.com/user-attachments/assets/f7c9add1-5ac6-417c-b4ca-f7a0df63797f
>>>>>>> 2b8b4ffe5b13f7ffd380d24842f4904d9f95b4cd


---
#### ✨ Features
- 📊 Intelligent Querying: Delivers precise answers to user questions based on scraped website content.
- 🌟 User-Friendly Design: An intuitive and engaging interface.
- ⚙️ Customizable & Scalable: Tailored to support various use cases and scalable across domains.

---
### Table of Contents

1. [Overview](#Overview)
2. [Core Functionality](#core-functionality)
3. [Technologies Used](#technologies-used)
4. [Demo](#Demo)
5. [Features](#Features)
6. [Requirements](#requirements)
7. [Installation](#installation)
8. [Project Structure](#project-structure)
9. [Usage](#usage)
10. [Endpoints](#endpoints)
11. [License](#license)
---

### Requirements

```bash
pip install -r requirements.txt
```

---

### Installation

### 1. Clone the repository:

```bash
git clone https://github.com/ManideepMuddagowni/TravelloFoodie---Your-Guide-Chatbot.git
cd TravelloFoodie - Your-Guide-Chatbot.git
```

### 2. Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` file in the root of the project and add your API key:

```plaintext
hf_token = ""
GROQ_API_KEY = ""
```

---

### Project Structure

The project follows a structured directory layout:TravelloFoodie - Your Guide -web-scraping
chatbot

![1732368401657](image/README/1732368401657.png)

---

### Usage

### 1. Start the server:

Run the server with:

```bash
uvicorn main:app --reload
```

This will start the API on `http://127.0.0.1:8000`. You can then interact with the chatbot through the provided frontend.

### 2. Start the server using FASTAPI

`uvicorn main:app --reload`

This will start the API on `http://127.0.0.1:8000/docs`. Insert the URL which you want to scrape in `/get_all_links/` [POST] You can then interact with the chatbot through the provided Swagger UI.

### 3. Open the frontend:

Open your browser and navigate to the provided URL to interact with the chatbot:

```
http://127.0.0.1:8000/
```

### 4. Ask questions:

The chatbot will retrieve answers based on the content scraped from the website, provided as part of the backend logic. The conversation is stored as a chat history, ensuring context is preserved during the conversation.

---

### Endpoints

### `/get_response/` [POST]

This endpoint generates a response to the user's question based on the scraped website content.

- **Request body**: JSON with a `question` field.

  ```json
  {
    "question": "What is Travello Foodie?"
  }
  ```
- **Response**: JSON with the AI-generated answer.

  ```json
  {
    "answer": "Travello Foodie is a travel and food guide platform..."
  }
  ```

### `/get_all_links/` [POST]

This endpoint fetches all internal links from a given URL. It scrapes the website and returns a list of links that are relevant for further scraping.

- **Request body**: JSON with a `question` field (URL).

  ```json
  {
    "question": "https://www.travellofoodie.com/"
  }
  ```
- **Response**: JSON with a list of internal links.

  ```json
  {
    "links": ["https://www.travellofoodie.com/about", "https://www.travellofoodie.com/destinations"]
  }
  ```

### `/static` [GET]

This serves static assets like CSS, JavaScript, and images for the chatbot frontend.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
