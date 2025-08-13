import uvicorn
from Loader.server import app
from Utils.V1.config_reader import configure

if __name__ == '__main__':
    uvicorn.run(app(), host=configure.get("SERVER", "HOST"), port=configure.getint("SERVER", "PORT"))
