from typing import Optional
from fastapi import FastAPI, Query
from backend.queries import get_logements

app = FastAPI(title="Student Housing API")

@app.get("/logements")
def logements(
    ville: Optional[str] = None,
    surface_min: Optional[float] = None,
    type_bien: Optional[str] = None,
    prix_max: Optional[int] = None
):
    df = get_logements(
        ville=ville,
        surface_min=surface_min,
        type_bien=type_bien,
        prix_max=prix_max
    )
    return df.to_dict(orient="records")
