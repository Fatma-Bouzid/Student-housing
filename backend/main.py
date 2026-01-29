from fastapi import FastAPI, Query
from backend.queries import get_logements

app = FastAPI(title="Student Housing API")

@app.get("/logements")
def logements(
    ville: str | None = None,
    surface_min: float | None = None,
    type_bien: str | None = None,
    prix_max: int | None = None
):
    df = get_logements(
        ville=ville,
        surface_min=surface_min,
        type_bien=type_bien,
        prix_max=prix_max
    )
    return df.to_dict(orient="records")
