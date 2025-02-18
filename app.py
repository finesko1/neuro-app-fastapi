from fastapi import FastAPI

app = FastAPI()

@app.get("/getInfo")
def read_root():
    return {"Hello": "World"}

@app.get("/helloWord")
def read_root():
    return {"Hello": "World"}

@app.get("/docs")
def read_doc():
    return 