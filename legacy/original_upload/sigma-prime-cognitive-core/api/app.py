from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from tools.sigma_prime.metrics import compute_sigma_prime


class SigmaRequest(BaseModel):
    phi: float = Field(ge=0)
    psi: float = Field(ge=0)
    epsilon: float = Field(ge=0)
    tau: float = Field(ge=0)
    eta: float = Field(ge=0)
    alpha: float = Field(ge=0)
    recurrence: float = Field(ge=0)


class SigmaResponse(BaseModel):
    sigma: float


app = FastAPI(title="Sigma-Prime API", version="0.1.0")


@app.get("/v1/healthz")
def healthz():
    return {"ok": True}


@app.post("/v1/sigma", response_model=SigmaResponse)
def sigma(req: SigmaRequest):
    try:
        val = compute_sigma_prime(
            req.phi, req.psi, req.epsilon, req.tau, req.eta, req.alpha, req.recurrence
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return SigmaResponse(sigma=val)
