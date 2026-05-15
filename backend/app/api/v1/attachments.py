from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.core.config import settings

router = APIRouter(tags=["attachments"])


@router.get("/attachments/proxy")
async def proxy_attachment(url: str) -> StreamingResponse:
    """
    Proxies attachment downloads from Chatwoot.
    
    Usage: /api/v1/attachments/proxy?url=<full_url_to_attachment>
    
    This endpoint:
    1. Fetches the file from Chatwoot
    2. Returns it with proper CORS headers
    3. Allows frontend to load cross-origin resources
    """
    if not url:
        raise HTTPException(status_code=400, detail="url parameter is required")
    
    # Security: only allow URLs from Chatwoot instance
    if not url.startswith(settings.chatwoot_base_url.rstrip("/")):
        raise HTTPException(
            status_code=403,
            detail="Only Chatwoot attachment URLs are allowed"
        )
    
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            
            # Determine content type from response headers or URL
            content_type = resp.headers.get("content-type", "application/octet-stream")
            
            # Get filename from URL or use default
            filename = url.split("/")[-1] or "attachment"
            
            return StreamingResponse(
                iter([resp.content]),
                status_code=200,
                media_type=content_type,
                headers={
                    "Content-Disposition": f'inline; filename="{filename}"',
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Cache-Control": "public, max-age=86400",  # Cache for 24h
                }
            )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Timeout fetching attachment from Chatwoot")
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Chatwoot returned {e.response.status_code}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching attachment: {str(e)}"
        )
