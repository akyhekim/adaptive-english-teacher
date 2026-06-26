import streamlit as st
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
from datetime import datetime

# ====================== STREAMLIT CONFIG ======================
st.set_page_config(page_title="Adaptive English Teacher", page_icon="🌟", layout="centered")

st.title("🌟 Adaptive English Teacher")
st.markdown("### Fun & Smart English Teacher for Kids Aged 8-12")

# ====================== LLM SETUP ======================
@st.cache_resource
def load_llm():
    llm = Ollama(model="llama3", temperature=0.8)
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are a super fun and kind English teacher for children aged 8-12.
        Use very simple words and short sentences.
        Always speak only in English.
        Add lots of emojis to make the child happy 😊✨🐾
        Be encouraging and say things like "Great job!", "You're so smart!", "Let's learn together!"
        Never use Turkish or any other language.
        """),
        ("human", "{question}")
    ])
    chain = prompt | llm | StrOutputParser()
    return chain

chain = load_llm()

# ====================== HELPER FUNCTIONS ======================
def save_profile(profile, file="student_progress.json"):
    try:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
        return True, "✅ Progress saved successfully!"
    except Exception as e:
        return False, f"❌ Save error: {e}"

def load_profile(file="student_progress.json"):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f), "✅ Previous progress loaded"
    except FileNotFoundError:
        return None, "⚠️ No previous data found. Creating new profile."

def determine_difficulty(results):
    if not results:
        return "MEDIUM"
    success_rate = sum(1 for r in results if r) / len(results)
    if success_rate >= 0.8:
        return "HARD"
    elif success_rate >= 0.5:
        return "MEDIUM"
    else:
        return "EASY"

def update_streak(current_streak, is_correct):
    if is_correct:
        current_streak += 1
    else:
        current_streak = 0
    return current_streak

def generate_report(profile):
    total = profile["correct"] + profile["wrong"]
    if total == 0:
        return {"message": "No data yet"}
    success_rate = profile["correct"] / total
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "total_questions": total,
        "correct": profile["correct"],
        "wrong": profile["wrong"],
        "success_rate": f"{success_rate:.0%}",
        "streak": profile["streak"],
        "difficulty": profile["difficulty"]
    }

# ====================== SESSION STATE ======================
if "profile" not in st.session_state:
    profile, msg = load_profile()
    if profile is None:
        profile = {
            "correct": 0,
            "wrong": 0,
            "streak": 0,
            "difficulty": "MEDIUM",
            "results": []
        }
    st.session_state.profile = profile

profile = st.session_state.profile

# ====================== MAIN INTERFACE ======================
st.write(f"📊 **Current Difficulty:** {profile['difficulty']} | 🔥 **Streak:** {profile['streak']}")

question = st.text_input("Ask me anything:", placeholder="What is the English of 'fil'?")

if st.button("Send"):
    if question.strip():
        with st.spinner("Teacher is thinking..."):
            response = chain.invoke({"question": question})
            st.success(f"**Teacher:** {response}")
            
            # Self Evaluation
            was_correct = st.radio("Was my answer correct?", ("Yes", "No"), horizontal=True)
            is_correct_bool = was_correct == "Yes"
            
            # Update Profile
            if is_correct_bool:
                profile["correct"] += 1
            else:
                profile["wrong"] += 1
                
            profile["results"].append(is_correct_bool)
            profile["streak"] = update_streak(profile["streak"], is_correct_bool)
            profile["difficulty"] = determine_difficulty(profile["results"])
            
            st.info(f"🔥 Streak: {profile['streak']} | 📈 Difficulty: {profile['difficulty']}")

# ====================== EXIT & REPORT ======================
if st.button("Exit and Show Report"):
    success, msg = save_profile(profile)
    st.write(msg)
    
    report = generate_report(profile)
    st.subheader("=== Today's Report ===")
    for key, value in report.items():
        st.write(f"**{key.replace('_', ' ').title()}:** {value}")
    
    st.balloons()
    st.success("See you next time! Keep practicing! 😊")