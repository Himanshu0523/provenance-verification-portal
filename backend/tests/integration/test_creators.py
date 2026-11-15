async def test_register_and_fetch(client):
    r = await client.post("/api/v1/creators",
                          json={"display_name": "Alice", "email": "a@x.io"})
    assert r.status_code == 201
    cid = r.json()["id"]

    r = await client.get(f"/api/v1/creators/{cid}")
    assert r.status_code == 200 and r.json()["display_name"] == "Alice"

async def test_get_unknown_creator_404(client):
    import uuid
    r = await client.get(f"/api/v1/creators/{uuid.uuid4()}")
    assert r.status_code == 404

async def test_duplicate_email_409(client):
    body = {"display_name": "Bob", "email": "dup@x.io"}
    assert (await client.post("/api/v1/creators", json=body)).status_code == 201
    r = await client.post("/api/v1/creators", json=body)
    assert r.status_code == 409