# backend/app/api/v1/router.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import datetime
import json # 用于处理无法序列化的请求体

from app.api.v1.endpoints import auth, users, navigation, push # 假设这些模块已创建

api_router_v1 = APIRouter()

# --- 包含各个模块的路由 ---
api_router_v1.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router_v1.include_router(users.router, prefix="/users", tags=["Users"])
api_router_v1.include_router(navigation.router, prefix="/navigation", tags=["Navigation"])
api_router_v1.include_router(push.router, prefix="/push", tags=["Push Notifications"])

# --- 通用调试接口 ---
@api_router_v1.api_route("/debug/echo", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def debug_echo(request: Request):
    """
    一个通用的回显接口，用于调试请求。
    返回请求的详细信息，包括方法、URL、头部、客户端IP和接收到的数据。
    """
    client_ip = request.client.host if request.client else "unknown"
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_local = datetime.datetime.now() # 服务器本地时间

    received_data = {}
    content_type = request.headers.get("content-type", "").lower()

    if request.method not in ["GET", "DELETE"]: # 对于有请求体的方法
        try:
            if "application/json" in content_type:
                received_data = await request.json()
            elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
                form_data = await request.form()
                received_data = dict(form_data)
            else:
                # 尝试读取为字节流，然后尝试解码为文本 (如果可能)
                body_bytes = await request.body()
                try:
                    received_data = {"raw_body_text": body_bytes.decode("utf-8")}
                except UnicodeDecodeError:
                    received_data = {"raw_body_base64": json.dumps(body_bytes.hex())} # Base64 编码或十六进制
        except json.JSONDecodeError:
            received_data = {"error": "Could not parse JSON body", "raw_body_text": (await request.body()).decode('utf-8', errors='replace')}
        except Exception as e:
            received_data = {"error": f"Could not parse request body: {str(e)}", "raw_body_text": (await request.body()).decode('utf-8', errors='replace')}
    else: # 对于 GET, DELETE，参数在 query_params 中
        received_data = dict(request.query_params)

    response_content = {
        "message": "Echo successful from yend2 debug endpoint!",
        "request_method": request.method,
        "request_url": str(request.url),
        "request_headers": dict(request.headers),
        "client_ip": client_ip,
        "received_data_or_params": received_data,
        "server_timestamp_utc": now_utc.isoformat(),
        "server_timestamp_local": now_local.isoformat(sep=' ', timespec='seconds'), # 更易读的本地时间
        "server_timestamp_epoch": now_utc.timestamp(),
    }
    return JSONResponse(content=response_content)