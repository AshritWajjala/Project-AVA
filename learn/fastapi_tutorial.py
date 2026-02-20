from fastapi import FastAPI

app = FastAPI()

status_json = {
    "Feeling": "Excited",
    "CPU": "AMD Ryzen 7 7800X3D",
    "GPU": "NVIDIA RTX 5080"
}
default_json = {
    "message": "BUDDY system online"
}

# Base page
@app.get('/')
def func():
    return default_json

# Status page
@app.get('/status')
def get_status():
    return status_json


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app=app, host='localhost', port=8000)