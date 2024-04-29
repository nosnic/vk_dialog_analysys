from fastapi import FastAPI

app = FastAPI()


@app.post("/auth")
def read_root(user_api: str):

    return {"message": "Hello World"}


@app.get("/generate_joke/")
def generate_joke():
    # Генерация шутки с помощью модели
    return {"joke": 'haha'}
