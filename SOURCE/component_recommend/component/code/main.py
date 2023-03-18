from fastapi import FastAPI, Request
# import uvicorn
from recommender import recommend_component
from distance_feature_extractor import training
app = FastAPI()
data_list = training(100000,100500)


@app.get("/")
async def Home():
    return {"Component recommendation system"}


@app.get("/recommend")
async def recommend(request: Request):
    try:
        data = await request.json()
    except Exception as e:
        print(e)
        data = []
    return recommend_component(data, data_list, k=5)
    
# if __name__ == '__main__':
    # uvicorn.run('main:app', host="127.0.0.1", port=80)
