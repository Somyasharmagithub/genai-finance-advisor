import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except:
    OPENAI_AVAILABLE = False


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY and OPENAI_AVAILABLE:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    client = None


st.title("💼 GenAI Finance Advisor")
st.write("Upload your business expense file (CSV)")


uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    
    st.subheader("📊 Expense Data")
    st.dataframe(df)

    
    st.subheader("📈 Expense by Category")
    category_expense = df.groupby("Category")["Amount"].sum()
    st.bar_chart(category_expense)

    
    
    st.subheader("📉 Monthly Expense Trend")
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    monthly_expense = df.groupby("Month")["Amount"].sum()
    st.line_chart(monthly_expense)

    
    st.subheader("📝 Business Summary")

    total_expense = df["Amount"].sum()
    highest_category = category_expense.idxmax()
    highest_category_amount = category_expense.max()

    summary_text = f"""
    • Total business expense is ₹{int(total_expense)}  
    • Highest spending category is **{highest_category}**  
    • Amount spent on {highest_category}: ₹{int(highest_category_amount)}
    """
    st.write(summary_text)

    
    st.markdown("---")
    st.subheader("🤖 AI Business Expense Advisor")

    user_question = st.text_input(
        "Ask a question about your business expenses",
        placeholder="e.g. Where can I reduce costs?"
    )

    if user_question:
        with st.spinner("Analyzing like a CFO..."):

            
            if client:
                try:
                    context = f"""
                    Total Expense: ₹{int(total_expense)}
                    Highest Category: {highest_category}
                    Amount: ₹{int(highest_category_amount)}

                    Category Breakdown:
                    {category_expense.to_string()}
                    """

                    prompt = f"""
                    You are a professional financial advisor.

                    Use the following business expense data to give
                    actionable advice.

                    DATA:
                    {context}

                    QUESTION:
                    {user_question}
                    """

                    response = client.responses.create(
                        model="gpt-5-mini",
                        input=prompt
                    )

                    answer = response.output_text

                except Exception:
                    
                    answer = None
            else:
                answer = None

            
            if answer is None:
                advice = []

                if highest_category_amount > 0.4 * total_expense:
                    advice.append(
                        f"• {highest_category} forms a large portion of expenses. Consider optimizing this category."
                    )

                if "marketing" in highest_category.lower():
                    advice.append(
                        "• Review marketing ROI. Focus on high-conversion channels and pause low-performing campaigns."
                    )

                if "rent" in category_expense.index.str.lower().to_list():
                    advice.append(
                        "• Explore remote or hybrid options to reduce fixed rental costs."
                    )

                advice.append(
                    "• Track expenses monthly and set budget limits per category."
                )

                advice.append(
                    "• Negotiate vendor contracts and subscriptions annually."
                )

                answer = "\n".join(advice)

        st.markdown("### 💡 Advisor Insights")
        st.write(answer)
