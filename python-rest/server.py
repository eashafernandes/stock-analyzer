import os
from fastapi import FastAPI
import importlib
import uvicorn
from config import PORT

app = FastAPI()

def setupplugins(app, path):
    path = os.path.join(path, 'routers')
    subfolders = [ dict(path=f.path, name = f.name) for f in os.scandir(path) if f.is_dir()]
    for subfolder in subfolders:
        fname = os.path.join(subfolder['path'], 'router.py')
        if not os.path.isfile(fname) : continue
        spec = importlib.util.spec_from_file_location(subfolder['name'], fname)
        router = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(router)
        app.include_router(router.router, prefix = f"/{subfolder['name']}")
    return app

path = os.path.dirname(os.path.abspath(__file__)) 
setupplugins(app, path)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT) #Incase python server.py is executed
