import streamlit as st
import google.generativeai as genai
import json
import os
from datetime import datetime

# --- CONFIGURATION ---
GEMINI_KEY   = "AIzaSyC2QopCfpySnQ9sNQrnc0UOVCC9hBQeFB4" # <--- PASTE YOUR KEY HERE
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')
DATA_FILE = "my_vocab.json"

# --- DATABASE LOGIC ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: return json.load(f)
    return {"words": [], "last_date": ""}

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f, indent=4)

# --- AI LOGIC: GENERATE 10 WORDS ---
def get_ai_words():
    prompt = "Give me 10 useful English words for an intermediate learner. For each word, provide: the word, the meaning, and 2 simple example sentences. Format as a JSON list of objects."
    response = model.generate_content(prompt)
    # Clean the AI text to get just the JSON
    raw_text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(raw_text)

# --- APP LAYOUT ---
st.set_page_config(page_title="English Buddy", page_icon="📖")
st.title("👨‍🏫 My English Buddy")

data = load_data()
today = datetime.now().strftime("%Y-%m-%d")

menu = st.sidebar.selectbox("Menu", ["Learn Today", "Quiz Mode", "Progress"])

if menu == "Learn Today":
    if data["last_date"] != today:
        if st.button("Generate Today's 10 Words"):
            with st.spinner("AI is thinking..."):
                new_words = get_ai_words()
                for w in new_words:
                    w["learned_on"] = today
                    w["score"] = 0 # for quiz tracking
                data["words"].extend(new_words)
                data["last_date"] = today
                save_data(data)
                st.rerun()
    
    # Display words learned today
    todays_list = [w for w in data["words"] if w.get("learned_on") == today]
    for i, w in enumerate(todays_list):
        with st.expander(f"{i+1}. {w['word']}"):
            st.write(f"**Meaning:** {w['meaning']}")
            st.write(f"**Sentence 1:** {w['sentence1'] if 'sentence1' in w else 'Check back later'}")
            st.write(f"**Sentence 2:** {w['sentence2'] if 'sentence2' in w else 'Check back later'}")

elif menu == "Quiz Mode":
    st.subheader("Test Your Memory!")
    if not data["words"]:
        st.write("Go learn some words first!")
    else:
        # Pick a random word from the whole list
        test_word = st.session_state.get("test_word", data["words"][0])
        st.header(test_word["word"])
        
        if st.button("Show Answer"):
            st.write(f"**Meaning:** {test_word['meaning']}")
            if st.button("Got it! Next ->"):
                st.session_state.test_word = data["words"][os.urandom(1)[0] % len(data["words"])]
                st.rerun()

elif menu == "Progress":
    st.write(f"Total words learned: {len(data['words'])}")
    st.table([{"Word": w["word"], "Date": w["learned_on"]} for w in data["words"]])
