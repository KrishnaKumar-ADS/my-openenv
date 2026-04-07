from __future__ import annotations
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import uvicorn
from server.routes import router

app = FastAPI(title="CustomerSupportEnv", description="OpenEnv-compliant benchmark", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)

@app.get("/", include_in_schema=False)
async def root():
	return RedirectResponse(url="/docs")

@app.get("/health")
async def health(): return {"status": "healthy", "env": "customer_support_env"}


def main() -> None:
	host = os.getenv("HOST", "0.0.0.0")
	port = int(os.getenv("PORT", "7860"))
	uvicorn.run("server.app:app", host=host, port=port)


if __name__ == "__main__":
	main()
