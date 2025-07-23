from fastapi import FastAPI


app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome to chatbot debate, go to /converstaion to get started"}

