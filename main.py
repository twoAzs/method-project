from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, String, Table, MetaData, select, and_
from sqlalchemy.orm import sessionmaker
from collections import deque

import redis
import json
import logging
import uvicorn
import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

try:
    cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    cache.ping()
except redis.exceptions.ConnectionError:
    cache = None

metadata = MetaData()

routes_table = Table(
    "routes", metadata,
    Column("origin", String, primary_key=True),
    Column("destination", String, primary_key=True)
)

engine = create_engine("sqlite:///./routes.db")
metadata.create_all(engine)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class RouteManager:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.graph = {}
        self._load_routes()

    def _load_routes(self):
        session = Session()
        results = session.execute(select(routes_table)).fetchall()
        session.close()
        for record in results:
            self.graph.setdefault(record.origin.upper(), set()).add(record.destination.upper())
            self.graph.setdefault(record.destination.upper(), set()).add(record.origin.upper())

    def bfs_shortest_path(self, start, end):
        if not start or not end:
            raise HTTPException(status_code=400, detail="invalid airport codes")

        start, end = start.upper(), end.upper()

        if start == end:
            return [start]

        if start not in self.graph:
            raise HTTPException(status_code=404, detail=f"No available route between {start} and {end}")
        if end not in self.graph:
            raise HTTPException(status_code=404, detail=f"No available route between {start} and {end}")

        cache_key = f"{min(start, end)}:{max(start, end)}"
        if cache:
            try:
                cached_path = cache.get(cache_key)
                if cached_path:
                    cache.expire(cache_key, 1800)
                    return json.loads(cached_path)
            except redis.exceptions.RedisError:
                print("redis error")
                pass

        queue = deque([(start, [start])])
        visited = set()

        while queue:
            node, path = queue.popleft()
            if node == end:
                if cache:
                    try:
                        cache.set(cache_key, json.dumps(path), ex=1800)
                    except redis.exceptions.RedisError:
                        pass
                return path
            if node in visited:
                continue

            visited.add(node)
            for neighbor in self.graph.get(node, []):
                queue.append((neighbor, path + [neighbor]))

        raise HTTPException(status_code=404, detail=f"No available route between {start} and {end}")

    def add_route(self, start, end):
        if not start or not end:
            raise HTTPException(status_code=400, detail="invalid airport codes")

        start, end = start.upper(), end.upper()

        with Session() as session, session.begin():
            if session.execute(select(routes_table).where(
                    and_(routes_table.c.origin == start, routes_table.c.destination == end))).fetchone():
                return False

            session.execute(routes_table.insert().values(origin=start, destination=end))
            session.execute(routes_table.insert().values(origin=end, destination=start))
            self.graph.setdefault(start, set()).add(end)
            self.graph.setdefault(end, set()).add(start)
        return True

    def clear_routes(self):
        session = Session()
        session.execute(routes_table.delete())
        session.commit()
        session.close()
        self.graph.clear()
        if cache:
            try:
                cache.flushdb()
            except redis.exceptions.RedisError:
                print("redis error")
                pass
        return True

app = FastAPI()
route_manager = RouteManager()

@app.post("/routes", status_code=201)
def create_route(route: dict):
    if not isinstance(route, dict) or "route" not in route or not isinstance(route["route"], list) or len(route["route"]) != 2:
        raise HTTPException(status_code=400, detail="invalid input")
    start, end = route["route"]
    if not route_manager.add_route(start, end):
        raise HTTPException(status_code=409, detail="route  exists")
    return {"message": "route added"}
#200 by success default
@app.get("/routes")
def get_shortest_route(start: str, end: str):
    return {"route": route_manager.bfs_shortest_path(start, end)}

@app.delete("/routes")
def clear_all_routes():
    route_manager.clear_routes()
    return {"message": "All routes removed"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7887, reload=True)
