from app.main import app


def test_analyze_endpoint_is_registered():
    """Keep the frontend upload contract tied to the real FastAPI route."""
    assert "post" in app.openapi()["paths"]["/api/analyze"]
