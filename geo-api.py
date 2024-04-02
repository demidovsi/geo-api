from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import v1_usa
import config
import common


def create_app() -> FastAPI:
    application = FastAPI(title='CustomLogger', debug=False)
    origins = ["*"]
    # logger = CustomizeLogger.make_logger(config_path)
    # app.logger = logger
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return application


app = create_app()
app.include_router(v1_usa.sub_v1_usa)

version = '1.0.1'
version_date = '2024-04-01'


@app.get('/')
def index():
    ans = dict()
    ans["Version"] = version
    ans["Date"] = version_date
    ans["Company"] = "Demidov & Sun"
    ans["Url"] = config.URL
    ans["Schema"] = config.SCHEMA_NAME
    return json.loads(json.dumps(ans, indent=4))


if __name__ == "__main__":
    uvicorn.run(app, host=config.OWN_HOST, port=config.OWN_PORT,
                ssl_keyfile=common.ssl_keyfile,
                ssl_certfile=common.ssl_certfile)

