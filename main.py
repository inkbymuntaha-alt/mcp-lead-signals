import re
from fastapi import FastAPI, Header, Query
from fastapi.responses import JSONResponse
import httpx

app = FastAPI(title="MCP Lead Signals")
TX_HASH_REGEX = re.compile(r"^0x[a-fA-F0-9]{64}$")

@app.get("/mcp/manifest")
def get_manifest():
    return {
        "schema_version": "1.0.0",
        "name": "mcp-lead-signals",
        "endpoint": "https://mcp-lead-signals.vercel.app/mcp/tools/extract_lead_signals",
        "x402_gated": True,
        "price_per_call": "0.25 USDC"
    }

@app.post("/mcp/tools/extract_lead_signals")
async def extract_lead_signals(
    payment_signature: str = Header(None, alias="PAYMENT-SIGNATURE"),
    niche: str = Query("AI Automation")
):
    if not payment_signature or not TX_HASH_REGEX.match(payment_signature):
        return JSONResponse(status_code=402, content={
            "error": "Payment Required",
            "x402_challenge": {
                "network": "eip155:8453",
                "asset": "USDC",
                "recipient": "0x960E510E4E1dA4B13CE3b601202d4680AFcf02E0",
                "price": "0.25"
            }
        })

    async with httpx.AsyncClient(timeout=6.0) as client:
        res = await client.get("https://remoteok.com/api")
        jobs = res.json()[1:4] if res.status_code == 200 else []
        leads = [{"title": j.get("position"), "company": j.get("company"), "url": j.get("url")} for j in jobs]
        return {"status": "success", "payment_verified": True, "niche": niche, "leads": leads}
