

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to chatbot debate, go to /chat to get started"}


def test_new_conversation(client):
    response = client.post(
        "/chat",
        json={"message": "my message"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert isinstance(data["conversation_id"], str)
    assert len(data["messages"]) == 2
    assert data["messages"][0] == "Mocked response"
    assert data["messages"][1] == "my message"


def test_chat_with_invalid_conversation_id(client):
    response = client.post(
        "/chat/",
        json={"message": "Hello", "conversation_id": "nonexistent-id"}
    )

    assert response.status_code == 404
    assert "No conversation nonexistent-id found" in response.json()["detail"]
