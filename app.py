import asyncio
import streamlit as st
from uagents import Agent, Context
from news_agent import bureau, reporter, NewsSummary, NewsResult

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

user = Agent(name="user", seed="user agent")

st.title("Echo Bot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        @user.on_interval(300.0)
        async def send_message(ctx: Context):
            await ctx.send(reporter.address, NewsSummary(query=prompt))

        bureau.add(user)
        bureau.run()
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
