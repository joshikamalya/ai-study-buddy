import streamlit as st
from groq import Groq
import json

st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="📘",
    layout="centered"
)

st.title("📘 AI Study Buddy")
st.caption("Your personal AI tutor to explain concepts, test understanding, and give feedback.")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "topic" not in st.session_state:
    st.session_state.topic = ""

if "explanation" not in st.session_state:
    st.session_state.explanation = ""

if "quiz" not in st.session_state:
    st.session_state.quiz = []

if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if "answers" not in st.session_state:
    st.session_state.answers = []

if "feedback" not in st.session_state:
    st.session_state.feedback = ""


def generate_explanation(topic):
    prompt = f"""
Explain the topic "{topic}" in a detailed and structured manner suitable for a computer science student.

Include:
- Definition
- Core concepts
- Examples
- Advantages and limitations
- Use cases
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are an expert academic tutor."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


def generate_quiz(explanation):
    prompt = f"""
Generate EXACTLY 3 multiple-choice questions based ONLY on the explanation below.

STRICT RULES:
- Output ONLY valid JSON
- Do NOT add explanations, markdown, or text
- Do NOT wrap in ``` or any formatting
- JSON must start with [ and end with ]

Format:
[
  {{
    "question": "Question text",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "Correct option text"
  }}
]

Explanation:
{explanation}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a strict JSON generator."},
            {"role": "user", "content": prompt}
        ]
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        st.error("⚠️ AI failed to generate quiz questions. Please click Start Learning again.")
        return []



def generate_feedback(topic, quiz, user_answers):
    prompt = f"""
Topic: {topic}

Quiz details:
{quiz}

User answers:
{user_answers}

Give constructive feedback with strengths, weaknesses, and improvement tips.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a supportive academic mentor."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


topic = st.text_input("Enter a topic to learn:")

if st.button("🚀 Start Learning"):
    if topic.strip() == "":
        st.warning("Please enter a valid topic.")
    else:
        st.session_state.topic = topic
        st.session_state.explanation = generate_explanation(topic)
        st.session_state.quiz = generate_quiz(st.session_state.explanation)
        st.session_state.current_q = 0
        st.session_state.answers = []
        st.session_state.feedback = ""


if st.session_state.explanation:
    st.subheader("📖 Explanation")
    st.markdown(st.session_state.explanation)


if st.session_state.quiz and st.session_state.current_q < len(st.session_state.quiz):

    q = st.session_state.quiz[st.session_state.current_q]

    st.subheader(f"📝 Question {st.session_state.current_q + 1}")
    st.write(q["question"])

    selected = st.radio(
        "Choose your answer:",
        q["options"],
        index=None,
        key=f"q_{st.session_state.current_q}"
    )

    if st.button("Submit Answer"):
        if selected is None:
            st.warning("Please select an option.")
        else:
            
            selected_clean = selected.strip().lower()
            correct_clean = q["answer"].strip().lower()

            st.session_state.answers.append({
                "question": q["question"],
                "selected": selected,
                "correct": q["answer"]
            })

            if selected_clean == correct_clean:
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect. Correct answer: {q['answer']}")

            st.session_state.current_q += 1
            st.rerun()


if st.session_state.quiz and st.session_state.current_q >= len(st.session_state.quiz):

    if not st.session_state.feedback:
        st.session_state.feedback = generate_feedback(
            st.session_state.topic,
            st.session_state.quiz,
            st.session_state.answers
        )

    st.subheader("📊 Feedback")
    st.markdown(st.session_state.feedback)
    st.success("🎉 Quiz completed! Keep learning 🚀")
