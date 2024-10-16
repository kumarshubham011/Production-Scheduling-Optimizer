import streamlit as st
# import openai
from groq import Groq
from typing import Generator
import pandas as pd
import plotly.express as px

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

    plot_type = st.selectbox("Selecg a plot type",
                             ['Bar Chart', 'Stacked Bar', 'Line Chart',
                              'Pie Chart', 'Box Plot'])

    # Create the selected plot
    if plot_type == 'Bar Chart':
        fig = px.bar(schedule_df.groupby('Machine')['Volume planned'].sum().reset_index(),
                     x='Machine', y='Volume planned', title='Total Volume Planned by Machine')
    elif plot_type == 'Stacked Bar':
        fig = px.bar(schedule_df, x='Machine', y='Volume planned', color='SKU',
                     title='Volume Planned by Machine and SKU')
    elif plot_type == 'Line Chart':
        fig = px.line(schedule_df, x='DATE', y='Volume planned', color='Machine',
                      title='Volume Planned Over Time by Machine')
    elif plot_type == 'Pie Chart':
        fig = px.pie(schedule_df, names='SKU', values='Volume planned',
                     title='Volume Planned by SKU')
    elif plot_type == 'Box Plot':
        fig = px.box(schedule_df, x='Machine', y='Volume planned',
                     title='Volume Planned by Machine')
    # ... (implement other plot types similarly)

    # Display the plot
    st.plotly_chart(fig)

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
            f"Optimize the production sequence for Machine {selected_machine} based on the following lead-time data:\n{machine_data}\n\n Provide the optimal sequence of SKUs to minimize lead-time. I just want the most optimized plan to switch from one sku to another on any given machine and not the explanation, just the final result. Treat it as a type of travelling salesman problem."
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
