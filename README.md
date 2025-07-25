# chatbot_debate

Simple chatbot api to debate with. 

The API consists of the following interface:

## ConversationSendMessageParams

```typescript
{
    "conversation_id": "text" | null,
    "message": "text"
}
```

## ConversationResponse

```typescript
{
    "conversation_id": "text",
    "message": [
        {
            "role": "user",
            "message": "text"
        },
        {
            "role": "bot",
            "message": "text"
        }
    ]
}
```

## Parameters

Parameters can customize the way LLM responds to the debate, leave empty to
use defaults

- api_key: string (deepseek api)
- base_url: string (deepsek url)
- model: string (deepseek-r1-0528)
- temperature: float (0.1)
- max_tokens: int (500)
- timeout: int (30s)

## How to run

### Requirements 

- [python](https://docs.docker.com/get-docker/)
- [docker](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)
- [uvicorn](https://www.uvicorn.org/)


### Available make commands:

  make install     - Install Python dependencies
  make test        - Run tests
  make run         - Run the app and services via Docker
  make down        - Stop services
  make clean       - Stop and remove all Docker containers, networks, and volumes

## Available live api 

### Fast api docs 

http://moned.cloud:8000/docs allows you to play with the available 
apis, make calls easily via a simple UI 

## Raw api

http://moned.cloud:8000/chat 

```
curl -X 'POST' \
  'http://moned.cloud:8000/chat/?api_key=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&base_url=https%3A%2F%2Fopenrouter.ai%2Fapi%2Fv1&model=deepseek%2Fdeepseek-r1-0528%3Afree&temperature=0.1&max_tokens=500&timeout=30' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "conversation_id": "2dfbe781-b0dc-4c3f-a4bc-786f5f6e809d",
  "message": "what about layoffs? that'\''s not good"
}'
```


