# ChatAgent Assignment Submission

## Introduction

I developed a command-line chatbot using the OpenRouter API. The chatbot supports multi-turn conversations through a rolling memory buffer and allows users to choose different language models before starting.

## Approach

The chatbot is implemented using a `ChatAgent` class that manages conversation history, handles API communication, and generates responses. Users can interact continuously until they enter `exit` or `quit`.

## Rolling Buffer

A rolling buffer stores only the most recent conversation turns. When the limit is exceeded, older messages are removed automatically. This reduces token usage, controls API costs, and prevents context overflow.

## Security

The API key is stored in a `.env` file and loaded through environment variables. The `.env` file is excluded from version control using `.gitignore` to protect sensitive credentials.

## Observations

The chatbot maintains context effectively within the buffer limit. Larger buffers improve memory retention but increase token consumption.

## Challenges

The main challenges were managing conversation history efficiently and keeping the implementation model-agnostic for easy model switching.

## Future Improvements

* Conversation summarization
* Streaming responses
* Chat history persistence
* Custom system prompts
* Web/GUI interface

## Conclusion

The chatbot successfully fulfills the assignment requirements by supporting model selection, multi-turn conversations, rolling memory, secure API key handling, and an object-oriented design.
