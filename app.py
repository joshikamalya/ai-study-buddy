import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="📘",
    layout="centered"
)

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama-3.1-8b-instant"

def get_ai_response(prompt):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"

def explanation_prompt(topic):
    return f"""
You are an AI study tutor.
Explain the topic "{topic}" in simple terms for a beginner.
Use short paragraphs.
"""

def quiz_prompt(topic):
    return f"""
Generate exactly 3 quiz questions on "{topic}".

Rules:
- Only show the questions
- If multiple-choice, show options A, B, C, D
- DO NOT show answers
- DO NOT give hints
"""

def evaluation_prompt(questions, answers):
    return f"""
You are a kind tutor.

Quiz Questions:
{questions}

Student Answers:
{answers}

Evaluate each answer.
Say Correct or Incorrect.
Give short feedback.
Encourage the student.
"""

st.markdown(
    """
    <h1 style='text-align: center;'>📘 AI Study Buddy</h1>
    <p style='text-align: center; font-size:18px;'>
    Your personal AI tutor for learning, quizzes, and feedback
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

st.subheader("📚 Start Learning")
topic = st.text_input(
    "Enter a topic",
    placeholder="e.g., Data Structure, Python, Machine Learning"
)

start = st.button("🚀 Start Learning", use_container_width=True)

if start:
    if topic.strip() == "":
        st.error("Please enter a topic")
    else:
        with st.spinner("Thinking..."):
            explanation = get_ai_response(explanation_prompt(topic))
            quiz = get_ai_response(quiz_prompt(topic))

        st.session_state.quiz = quiz

        st.markdown("### 📖 Explanation")
        st.info(explanation)

        st.markdown("### 📝 Quiz")
        st.warning(quiz)

if "quiz" in st.session_state:
    st.markdown("### ✍️ Your Answers")

    a1 = st.radio("Question 1", ["A","B","C","D"], horizontal=True)
    a2 = st.radio("Question 2", ["A","B","C","D"], horizontal=True)
    a3 = st.radio("Question 3", ["A","B","C","D"], horizontal=True)
    submit = st.button("✅ Submit Answers", use_container_width=True)

    if submit:
        answers = f"""
1. {a1}
2. {a2}
3. {a3}
"""
        with st.spinner("Evaluating your answers..."):
            feedback = get_ai_response(
                evaluation_prompt(st.session_state.quiz, answers)
            )

        st.markdown("### 📊 Feedback")
        st.success(feedback)

