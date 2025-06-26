from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse, PlainTextResponse
import httpx
from typing import Dict
app = FastAPI()

SERVERS: Dict[str, str] = {
    "linkup": "http://localhost:8081",
    "mem0": "http://localhost:8082",
    "spotify": "http://localhost:8083",
}


@app.get("/{server_id}/sse")
async def stream_sse(server_id: str):
    base_url = SERVERS.get(server_id)
    if not base_url:
        raise HTTPException(status_code=404, detail="Unknown server ID")

    url = f"{base_url}/sse"
    client = httpx.AsyncClient(timeout=None)

    async def event_stream():
        try:
            async with client.stream("GET", url) as resp:
                buffer = []
                async for line in resp.aiter_lines():
                    if line == "":
                        # End of event, process and yield
                        event = "\n".join(buffer)
                        event = event.replace("/messages", f"/{server_id}/messages")
                        yield f"{event}\n\n"
                        buffer = []
                    else:
                        buffer.append(line)
                # Yield any remaining buffer
                if buffer:
                    event = "\n".join(buffer)
                    event = event.replace("/messages", f"/{server_id}/messages")
                    yield f"{event}\n\n"
        except Exception as e:
            print(f"SSE error: {e}")
            yield f"event: error\ndata: SSE stream error\n\n"

    try:
        return StreamingResponse(event_stream(), media_type="text/event-stream")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/{server_id}/messages/")
async def post_sse(server_id: str, request: Request):
    base_url = SERVERS.get(server_id)
    if not base_url:
        raise HTTPException(status_code=404, detail="Unknown server ID")

    url = f"{base_url}/messages/"
    data = await request.json()
    session_id = request.query_params.get("session_id")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=data, params={"session_id": session_id})
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")
    try:
        return JSONResponse(resp.json())
    except Exception:
        return PlainTextResponse(resp.text, status_code=resp.status_code)

if __name__ == "__main__":
    import uvicorn
    print("Starting MCP Hub")

    uvicorn.run("mcp_hub:app", host="0.0.0.0", port=7000, reload=0)