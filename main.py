import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq
from typing import Generator

st.set_page_config(page_title="Schedule optimizer", layout='wide',)

# Title of the app
st.title("Generative AI Production Scheduling Optimizer")

# Upload CSV files
production_schedule = st.file_uploader(
    "Upload Production Schedule EXCEL", type="xlsx")
lead_time_data = st.file_uploader("Upload Change-Over-Time EXCEL", type="xlsx")

if production_schedule and lead_time_data:
    # Read the data
    schedule_df = pd.read_excel(production_schedule)
    lead_time_df = pd.read_excel(lead_time_data)

    # Display uploaded data
    st.write("Production Schedule Data:", schedule_df.head())
    st.write("Change-Over-Time Data:", lead_time_df.head())

    # Visualization
    plot_type = st.selectbox("Select a plot type", [
                             'Bar Chart', 'Stacked Bar', 'Line Chart', 'Pie Chart', 'Box Plot'])

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

    st.plotly_chart(fig)

    # Machine selection
    machines = lead_time_df['Machine'].unique()
    selected_machine = st.selectbox(
        "Select a Machine for Optimization", machines)

    # Initialize Groq API (replace with actual key)
    client = Groq(
        api_key="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")

    # Maintaining session history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
        """Yield chat response content from the Groq API response."""
        for chunk in chat_completion:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    # If a machine is selected, show the result
    if selected_machine:
        machine_data = lead_time_df[lead_time_df['Machine']
                                    == selected_machine]
        machine_data.drop('Machine', axis=1, inplace=True)

        # Create the prompt for the selected machine
        # machine_prompt = (
        #     f"Based on the production schedule and lead-time data for Machine {selected_machine}, optimize the production sequence "
        #     f"and restrict the responses only to the following provided data:\n"
        #     # f"Production Schedule:\n{schedule_df.to_string(index=False)}\n\n"
        #     f"Lead-Time Data:\n{machine_data.to_string(index=False)}\n\n"
        #     "Provide the optimal sequence of SKUs to minimize lead-time, considering only the provided information. For each machine do not consider the column 'DATE', 'Week', 'Volume planned'. Give the final result (without any code) in a neat, easy to understand format while. You can use algorithms like gentic algorithm, brute force approach etc. to do this task."
        # )

        # Update the machine prompt with the desired output format
        machine_prompt = (
            f"Based on the production schedule and lead-time data for Machine {selected_machine}, optimize the production sequence "
            f"and restrict the responses only to the following provided data:\n"
            f"Lead-Time Data:\n{machine_data.to_string(index=False)}\n\n"
            # "Provide the optimal sequence of SKUs to minimize lead-time, considering only the provided information. "
            # "Use optimization techniques to give me the shortest total time to cover all the SKU once. "
            "Provide the optimal sequence of SKUs to minimize lead-time, considering only the provided information. "
            "Use brute force optimization technique to give me the shortest total time to cover all the SKU once. "
            "Ensure that the response is presented in the following format:\n\n"
            "### Optimized Production Schedule for Machine {selected_machine}\n"
            "1. **Sequence of SKUs:** SKU1 -> SKU2 -> SKU3 -> ...\n"
            "2. **Total Lead-Time:** [Calculated value here]\n"
            "3. **Key Observations:**\n"
            "- [Observation 1]\n"
            "- [Observation 2]\n\n"
            "Output only in this format and do not include 'Notes' in your responses."
        )

        # Update the machine prompt with the desired output format
        # machine_prompt = (
        #     f"Based on the production schedule and lead-time data for Machine {selected_machine}, optimize the production sequence "
        #     f"and restrict the responses only to the following provided data:\n"
        #     f"Lead-Time Data:\n{machine_data.to_string(index=False)}\n\n"
        #     # "Provide the optimal sequence of SKUs to minimize lead-time, considering only the provided information. "
        #     # "Use optimization techniques to give me the shortest total time to cover all the SKU once. "
        #     "Provide the optimal sequence of SKUs to minimize lead-time, considering only the provided information. "
        #     "Use optimization techniques to give me the shortest total time to cover all the SKU once. "
        #     "Ensure that the response is presented in the following format:\n\n"
        #     "### Optimized Production Schedule for Machine {selected_machine}\n"
        #     "1. **Sequence of SKUs:** SKU1 -> SKU2 -> SKU3 -> ...\n"
        #     "2. **Total Lead-Time:** [Calculated value here]\n"
        #     "3. **Key Observations:**\n"
        #     "- [Observation 1]\n"
        #     "- [Observation 2]\n\n"
        # "Output only in this format and do not include 'Notes' in your responses."
        # )

        # machine_prompt = (
        #     f"Based on the production schedule and lead-time data for Machine {selected_machine}, optimize the production sequence "
        #     f"and restrict the responses only to the following provided data:\n"
        #     f"Lead-Time Data:\n{machine_data.to_string(index=False)}\n\n"
        #     "The changeover time data has the following columns: Machine, SKU_1, SKU_2, and Changeover Time from SKU_1 to SKU_2. "
        #     "Provide the optimal sequence of all SKUs for the selected machine to minimize total changeover time, considering only the provided information. "
        #     "Use optimization techniques to give me the shortest total changeover time to cover all the SKUs once. "
        #     "Ensure that the response is presented in the following format:\n\n"
        #     "### Optimized Production Schedule for Machine {selected_machine}\n"
        #     "1. **Sequence of SKUs:** SKU1 -> SKU2 -> SKU3 -> ...\n"
        #     "2. **Total Changeover Time:** [Calculated value here]\n"
        #     "3. **Key Observations:**\n"
        #     "- [Observation 1]\n"
        #     "- [Observation 2]\n\n"
        #     "Output only in this format and do not include 'Notes' in your responses. Do not change the answers or hallucinate."
        # )

        # Add machine prompt to session history
        st.session_state.messages.append(
            {"role": "user", "content": machine_prompt})

        # Send the entire chat history, including past responses and prompts, to the LLM for context
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[{"role": m["role"], "content": m["content"]}
                          for m in st.session_state.messages],
                temperature=0,
                max_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
            )

            # Show chat history
            for message in st.session_state.messages:
                avatar = '🤖' if message["role"] == "assistant" else '👨‍💻'
                with st.chat_message(message["role"], avatar=avatar):
                    st.markdown(message["content"])

            # Use the generator function to yield responses
            chat_responses_generator = generate_chat_responses(completion)
            response = st.write_stream(chat_responses_generator)

        except Exception as e:
            st.write(f"Error: {e}")

    # Allow user to interact and ask more questions
    if user_input := st.chat_input("Ask about the optimized schedule or other questions..."):
        st.session_state.messages.append(
            {"role": "user", "content": user_input})

        # Modify user input to restrict response to uploaded data
        modified_user_input = (
            f"{user_input}\n"
            f"Restrict your response only to the data provided in the production schedule and lead-time files:\n"
            f"Production Schedule:\n{schedule_df.to_string(index=False)}\n\n"
            f"Lead-Time Data:\n{lead_time_df.to_string(index=False)}"
        )

        # Overwrite the last user input with restricted version
        st.session_state.messages[-1]['content'] = modified_user_input

        with st.chat_message("user", avatar='👨‍💻'):
            st.markdown(user_input)

        # Generate response from Groq API
        try:
            chat_completion = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[{"role": m["role"], "content": m["content"]}
                          for m in st.session_state.messages],  # Pass full conversation context
                max_tokens=1024,
                temperature=0,
                stream=True
            )

            # Use the generator function to display responses
            with st.chat_message("assistant", avatar="🤖"):
                chat_responses_generator = generate_chat_responses(
                    chat_completion)
                full_response = st.write_stream(chat_responses_generator)

            # Append the full response to session state
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Error: {e}", icon="🚨")
