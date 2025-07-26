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

### Instructions 

1. Create .env file in the root folder
2. Add env variable OPENROUTER_API_KEY with an open router api key
3. `make install && make run ` - In case docker requires root permissions, run with `sudo`
4. Send curl request

```
curl -X 'POST' \
  'http://localhost:8000/chat/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "message": "what about layoffs? that'\''s not good"
}'
```


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


# Examples 

## New conversation

### Chat completion

Request: 
```
curl -X 'POST' \
  'http://moned.cloud:8000/chat/?base_url=https%3A%2F%2Fopenrouter.ai%2Fapi%2Fv1&model=deepseek%2Fdeepseek-r1-0528%3Afree&temperature=0.1&max_tokens=500&timeout=30' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "message": "I can see buildings really far away, so I think earth is flat"
}'
```

Response:
```
{
  "conversation_id": "24a78483-9704-4a5e-9891-59ee26d6aec9",
  "message": [
    {
      "role": "bot",
      "message": "That's incorrect because Earth's curvature limits visibility beyond 10-15 miles. Ships disappear hull-first over the horizon, which wouldn't occur on a flat plane. This proves the planet is spherical."
    },
    {
      "role": "user",
      "message": "I can see buildings really far away, so I think earth is flat"
    }
  ]
}
```


### Chat stream

Request: 
```
curl -X 'POST' \
  'http://moned.cloud:8000/chat/stream?base_url=https%3A%2F%2Fopenrouter.ai%2Fapi%2Fv1&model=deepseek%2Fdeepseek-r1-0528%3Afree&temperature=0.1&max_tokens=500&timeout=30' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "message": "I can see buildings really far away, so I think earth is flat"
}'
```

Response:
```
event: start

data: {"conversation_id": "745ac140-5128-40ee-a042-cc05b0d5ce97", "message": "That's incorrect because distant ships disappear hull-first over the horizon, which wouldn't occur on", "role": "bot", "part": 1}

data: {"conversation_id": "745ac140-5128-40ee-a042-cc05b0d5ce97", "message": " a flat surface.", "role": "bot", "part": 2}

data: {"conversation_id": "745ac140-5128-40ee-a042-cc05b0d5ce97", "message": " For example, lighthouses visible from 40 miles away at high altitudes vanish completely at sea level", "role": "bot", "part": 3}

data: {"conversation_id": "745ac140-5128-40ee-a042-cc05b0d5ce97", "message": " due to Earth's curvature.", "role": "bot", "part": 4}

data: {"conversation_id": "745ac140-5128-40ee-a042-cc05b0d5ce97", "message": " This proves the planet is spherical, not flat.", "role": "bot", "part": 5}

data: {"conversation_id": "745ac140-5128-40ee-a042-cc05b0d5ce97", "message": [{"role": "bot", "message": "That's incorrect because distant ships disappear hull-first over the horizon, which wouldn't occur on a flat surface. For example, lighthouses visible from 40 miles away at high altitudes vanish completely at sea level due to Earth's curvature. This proves the planet is spherical, not flat."}, {"role": "user", "message": "I can see buildings really far away, so I think earth is flat"}], "part": "final"}

event: end


```


## Continue conversation 

### Chat completion 

Request:
```
curl -X 'POST' \
  'http://moned.cloud:8000/chat/?base_url=https%3A%2F%2Fopenrouter.ai%2Fapi%2Fv1&model=deepseek%2Fdeepseek-r1-0528%3Afree&temperature=0.1&max_tokens=500&timeout=30' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "conversation_id": "24a78483-9704-4a5e-9891-59ee26d6aec9",
  "message": "But the horizon is a flat line"
}'
```

Response:
```
{
  "conversation_id": "24a78483-9704-4a5e-9891-59ee26d6aec9",
  "message": [
    {
      "role": "bot",
      "message": "That perception is misleading because the horizon only appears flat due to limited human vision at ground level. When observed from high altitudes like aircraft or mountains, the visible curvature becomes undeniable, as demonstrated by countless aerial photographs. This directly confirms Earth's spherical shape."
    },
    {
      "role": "user",
      "message": "But the horizon is a flat line"
    },
    {
      "role": "bot",
      "message": "That's incorrect because Earth's curvature limits visibility beyond 10-15 miles. Ships disappear hull-first over the horizon, which wouldn't occur on a flat plane. This proves the planet is spherical."
    },
    {
      "role": "user",
      "message": "I can see buildings really far away, so I think earth is flat"
    }
  ]
}
```

### Chat stream

Request:
```
curl -X 'POST' \
  'http://moned.cloud:8000/chat/stream?base_url=https%3A%2F%2Fopenrouter.ai%2Fapi%2Fv1&model=deepseek%2Fdeepseek-r1-0528%3Afree&temperature=0.1&max_tokens=500&timeout=30' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "conversation_id": "745ac140-5128-40ee-a042-cc05b0d5ce97",
  "message": "But the horizon is a flat line"
}'
```

Response:
```
event: start

data: {"conversation_id": "745ac140-5128-40ee-a042-cc05b0d5ce97", "message": "That claim ignores how perspective works on a spherical surface.", "role": "bot", "part": 1}

data: {"conversation_id": "745ac140-5128-40ee-a042-cc05b0d5ce97", "message": " For instance, astronauts observe a distinctly curved horizon from space stations, while ground observers", "role": "bot", "part": 2}

data: {"conversation_id": "745ac140-5128-40ee-a042-cc05b0d5ce97", "message": " see only a small segment that appears flat due to scale.", "role": "bot", "part": 3}

data: {"conversation_id": "745ac140-5128-40ee-a042-cc05b0d5ce97", "message": " This visual limitation doesn't negate global curvature demonstrated by satellite imagery.", "role": "bot", "part": 4}

data: {"conversation_id": "745ac140-5128-40ee-a042-cc05b0d5ce97", "message": [{"role": "bot", "message": "That claim ignores how perspective works on a spherical surface. For instance, astronauts observe a distinctly curved horizon from space stations, while ground observers see only a small segment that appears flat due to scale. This visual limitation doesn't negate global curvature demonstrated by satellite imagery."}, {"role": "user", "message": "But the horizon is a flat line"}, {"role": "bot", "message": "That's incorrect because distant ships disappear hull-first over the horizon, which wouldn't occur on a flat surface. For example, lighthouses visible from 40 miles away at high altitudes vanish completely at sea level due to Earth's curvature. This proves the planet is spherical, not flat."}, {"role": "user", "message": "I can see buildings really far away, so I think earth is flat"}], "part": "final"}

event: end

```


