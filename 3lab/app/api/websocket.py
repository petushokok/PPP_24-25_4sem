from fastapi import WebSocket, WebSocketDisconnect
import redis.asyncio as redis
import json

r = redis.Redis(host="redis", port=6379)


async def websocket_progress(ws: WebSocket, task_id: str):
    await ws.accept()
    pubsub = r.pubsub()
    await pubsub.subscribe(f"progress:{task_id}")

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                await ws.send_json(data)
    except WebSocketDisconnect:
        print(f"WebSocket closed by client for task {task_id}")

    except Exception as e:
        print(f"Unexpected error in websocket for task {task_id}: {e}")

    finally:
        await pubsub.unsubscribe(f"progress:{task_id}")
        await ws.close()
