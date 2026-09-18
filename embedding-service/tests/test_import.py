def test_import():
    from app.main import app
    assert app.title == "RAG Embedding Service"
