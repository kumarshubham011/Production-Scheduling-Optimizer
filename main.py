import streamlit as st
# import openai
from groq import Groq
from typing import Generator
import pandas as pd

st.title("Generative AI Production Scheduling Optimizer for Multiple Machines")

# Upload CSV files
production_schedule = st.file_uploader(
    "Upload Production Schedule EXCEL", type="xlsx")
lead_time_data = st.file_uploader("Upload Lead-Time EXCEL", type="xlsx")

if production_schedule and lead_time_data:
    schedule_df = pd.read_excel(production_schedule)
    lead_time_df = pd.read_excel(lead_time_data)

    # Display uploaded data
    st.write("Production Schedule Data:", schedule_df.head())
    st.write("Lead-Time Data:", lead_time_df.head())

    # Get unique machines for dropdown selection
    machines = lead_time_df['Machine'].unique()
    selected_machine = st.selectbox("Select a Machine", machines)

    # Initialize OpenAI API
    # openai.api_key = ''

    # Display selected machine's data
    if selected_machine:
        machine_data = lead_time_df[lead_time_df['Machine']
                                    == selected_machine]

        # Create the prompt with selected machine's lead-time data
        # lead_time_summary = machine_data.to_string(index=False)
        machine_data.drop('Machine', axis=1, inplace=True)
        machine_prompt = (
            f"Optimize the production sequence for Machine {selected_machine} based on the following lead-time data:\n{machine_data}\n\n Provide the optimal sequence of SKUs to minimize lead-time. I just want the most optimized plan to switch from one sku to another on any given machine and not the explanation, just the final result"
        )

        # Display the prompt (for debugging)
        st.write(machine_prompt)

        # GPT API call with error handling
        try:
            client = Groq(
                api_key="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")

            completion = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": machine_prompt,
                    }
                ],
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
            )

            def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
                """Yield chat response content from the Groq API response."""
                for chunk in chat_completion:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            # for chunk in completion:
            #     print(chunk.choices[0].delta.content or "", end="")

            # Display the result for the selected machine
            # st.write(
            #     f"Optimized SKU Sequence for Machine {selected_machine}:", response.choices[0].text.strip())
            chat_responses_generator = generate_chat_responses(completion)
            st.write_stream(chat_responses_generator)

        except Exception as e:
            st.write(e)
