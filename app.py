import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
import cohere

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Smart Fitness Pro", layout="centered")

# ---------------- UI ----------------
st.markdown("""
<style>
.stApp { background-color: #ffffff; color: #000000; }
h1,h2,h3 { color: #2563eb; }

.stButton>button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
}

.center-text {
    text-align: center;
    font-size: 20px;
    margin-top: 100px;
    color: gray;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN ----------------
users = {"gireesh": "1234", "admin": "python"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u in users and users[u] == p:
            st.session_state.logged_in = True
            st.session_state.user = u
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()

# ---------------- FUNCTIONS ----------------
def bmi(weight, height):
    return weight / ((height/100) ** 2)

def bmi_category(b):
    if b < 18.5:
        return "Underweight"
    elif b < 25:
        return "Normal"
    else:
        return "Overweight"

def calories(weight, goal):
    base = weight * 30
    if goal == "Fat Loss":
        return base - 500
    elif goal == "Bulking":
        return base + 300
    return base - 300

def macros(weight, goal):
    if goal == "Fat Loss":
        return weight*1.8, weight*2, weight*0.8
    elif goal == "Bulking":
        return weight*2, weight*3, weight*1
    return weight*1.6, weight*2.5, weight*0.8

def water(weight):
    return weight * 0.035

# ---------------- MAIN ----------------
st.title("🏋️ Smart Fitness Pro")
st.write(f"Welcome, {st.session_state.user} 👋")

tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Profile",
    "🤖 AI Plan",
    "💬 Gym AI",
    "📊 Progress"
])

# -------- TAB 1 --------
with tab1:
    st.subheader("👤 User Profile")

    st.session_state.name = st.text_input("Name")
    st.session_state.age = st.number_input("Age", 0, 100)
    st.session_state.height = st.number_input("Height (cm)", 0, 250)
    st.session_state.weight = st.number_input("Weight (kg)", 0, 200)

    if st.button("Calculate BMI"):
        b = bmi(st.session_state.weight, st.session_state.height)
        st.success(f"BMI: {b:.2f} ({bmi_category(b)})")

# -------- TAB 2 --------
with tab2:
    st.subheader("🎯 Personalized Plan")

    goal = st.selectbox("Goal", ["Fat Loss", "Bulking", "Cutting"])

    if st.button("Generate Plan"):
        b = bmi(st.session_state.weight, st.session_state.height)
        cal = calories(st.session_state.weight, goal)
        p,c,f = macros(st.session_state.weight, goal)

        st.info(f"Calories: {cal} kcal")
        st.write(f"Protein: {p:.1f}g | Carbs: {c:.1f}g | Fat: {f:.1f}g")
        st.write(f"💧 Water: {water(st.session_state.weight):.2f} L")

# -------- TAB 3 (AI FIXED) --------
with tab3:

    st.markdown(
        '<div class="center-text">💬 Feel free to ask anything about your gym goal</div>',
        unsafe_allow_html=True
    )

 import streamlit as st
co = cohere.Client(st.secrets["1znqOOQlmBMGbe6HKOyhB6DiBjvyAPtrSVSp5j0A"])



    def query_cohere(prompt):
        try:
            response = co.chat(
                model="command-a-03-2025",   # ✅ correct working model
                message=prompt
            )
            return response.text
        except Exception as e:
            return f"Error: {e}"

    if "chat" not in st.session_state:
        st.session_state.chat = []

    for role, msg in st.session_state.chat:
        if role == "user":
            st.chat_message("user").write(msg)
        else:
            st.chat_message("assistant").write(msg)

    user_input = st.chat_input("Ask about workouts, diet, gym plans...")

    if user_input:
        st.session_state.chat.append(("user", user_input))
        st.chat_message("user").write(user_input)

        bmi_info = ""
        if "weight" in st.session_state:
            bmi_info = f"My weight is {st.session_state.weight}kg and height is {st.session_state.height}cm."

        full_prompt = f"{bmi_info} User says: {user_input}"

        with st.spinner("AI is thinking..."):
            answer = query_cohere(full_prompt)

        st.session_state.chat.append(("bot", answer))
        st.chat_message("assistant").write(answer)

# -------- TAB 4 --------
with tab4:
    st.subheader("📊 Workout Progress Tracker")

    if "name" not in st.session_state or st.session_state.name == "":
        st.warning("⚠️ Fill profile first")
        st.stop()

    entry_date = st.date_input("Date", date.today())
    workout = st.text_input("Workout")
    sets = st.number_input("Sets", 1, 50)
    reps = st.number_input("Repetitions", 1, 100)
    calories_burned = st.number_input("Calories Burned", 0, 5000)

    # -------- SAVE --------
    if st.button("Save Entry"):
        new = {
            "name": st.session_state.name,
            "age": st.session_state.age,
            "weight": st.session_state.weight,
            "height": st.session_state.height,
            "date": entry_date,
            "workout": workout,
            "sets": sets,
            "repetitions": reps,
            "calories": calories_burned
        }

        try:
            df = pd.read_csv("progress.csv")
        except FileNotFoundError:
            df = pd.DataFrame(columns=new.keys())

        df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
        df.to_csv("progress.csv", index=False)
        st.success("Saved ✅")

    # -------- LOAD --------
    try:
        df = pd.read_csv("progress.csv")

        st.write("### 📋 Data Table")
        df_display = df.copy()
        df_display.insert(0, "S.No", range(1, len(df_display) + 1))
        st.dataframe(df_display, use_container_width=True)

        # -------- DELETE BUTTONS --------
        st.write("### 🗑️ Delete Entry")
        for i in range(len(df)):
            cols = st.columns([1,8])
            if cols[0].button("🗑️", key=f"del_{i}"):
                df = df.drop(i).reset_index(drop=True)
                df.to_csv("progress.csv", index=False)
                st.success("Deleted ✅")
                st.rerun()
            cols[1].write(
                f"{i+1}. {df.loc[i,'date']} | {df.loc[i,'name']} | {df.loc[i,'workout']} | {df.loc[i,'calories']} cal"
            )

        # -------- MATPLOTLIB GRAPH --------
        st.write("### 📊 Calories Graph")
        if st.button("Plot Graph"):
            for person in df["name"].unique():
                person_df = df[df["name"] == person]

                fig, ax = plt.subplots(figsize=(6,4))  # ✅ smaller graph
                ax.bar(person_df["date"], person_df["calories"], color="skyblue")

                ax.set_title(f"{person}'s Calories Burned")
                ax.set_xlabel("Date")
                ax.set_ylabel("Calories")

                # Show values on hover-like labels
                for i, val in enumerate(person_df["calories"]):
                    ax.text(i, val + 5, str(val), ha="center")

                st.pyplot(fig)

    except FileNotFoundError:
        st.warning("No data yet")
