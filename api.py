from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from langchain_core.messages import HumanMessage

from chatBot_backend import (
    ChatBot,
    get_all_thread_id,
)

app = FastAPI(
    title="LangGraph ChatBot API",
    version="1.0.0"
)


# ==========================================================
# Request Model
# ==========================================================

class ChatRequest(BaseModel):
    message: str
    thread_id: str


# ==========================================================
# Root
# ==========================================================

@app.get("/")
def root():
    return {
        "status": "running",
        "message": "LangGraph ChatBot API"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ==========================================================
# Get all thread ids
# ==========================================================

@app.get("/threads")
def threads():

    return {
        "threads": get_all_thread_id()
    }


# ==========================================================
# Get one conversation
# ==========================================================

@app.get("/threads/{thread_id}")
def get_thread(thread_id: str):

    try:

        state = ChatBot.get_state(
            config={
                "configurable": {
                    "thread_id": thread_id
                }
            }
        )

        messages = state.values.get("messages", [])

        conversation = []

        for msg in messages:

            if msg.type == "human":
                role = "user"
            else:
                role = "assistant"

            conversation.append(
                {
                    "role": role,
                    "content": msg.content
                }
            )

        return conversation

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==========================================================
# Normal Chat
# ==========================================================

@app.post("/chat")
def chat(request: ChatRequest):

    try:

        config = {
            "configurable": {
                "thread_id": request.thread_id
            }
        }

        response = ChatBot.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=request.message
                    )
                ]
            },
            config=config,
        )

        return {
            "response": response["messages"][-1].content
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==========================================================
# Streaming Chat
# ==========================================================

@app.post("/stream")
def stream_chat(request: ChatRequest):

    config = {
        "configurable": {
            "thread_id": request.thread_id
        }
    }

    def generate():

        try:

            for message_chunk, metadata in ChatBot.stream(
                {
                    "messages": [
                        HumanMessage(
                            content=request.message
                        )
                    ]
                },
                config=config,
                stream_mode="messages",
            ):

                if message_chunk.content:
                    yield message_chunk.content

        except Exception as e:

            yield f"\nERROR: {str(e)}"

    return StreamingResponse(
        generate(),
        media_type="text/plain",
    )