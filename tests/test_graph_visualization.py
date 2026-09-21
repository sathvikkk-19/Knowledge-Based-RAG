import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.api import app
from app.graph.graph_retriever import GraphRetriever


def test_graph_retriever_get_graph_data():
    print("=" * 80)
    print("TEST GRAPH RETRIEVER GET_GRAPH_DATA")
    print("=" * 80)

    retriever = GraphRetriever()
    try:
        data = retriever.get_graph_data(limit=50)
        assert "nodes" in data
        assert "links" in data
        assert isinstance(data["nodes"], list)
        assert isinstance(data["links"], list)
        print(f"Retrieved {len(data['nodes'])} nodes and {len(data['links'])} links.")

        if data["nodes"]:
            first_node = data["nodes"][0]
            assert "id" in first_node
            assert "name" in first_node
            assert "entity_type" in first_node
            print(f"Sample node: {first_node}")

        if data["links"]:
            first_link = data["links"][0]
            assert "source" in first_link
            assert "target" in first_link
            assert "relationship" in first_link
            print(f"Sample link: {first_link}")

        print("GraphRetriever get_graph_data test PASSED!")
    finally:
        retriever.close()


def test_api_graph_endpoint():
    print("=" * 80)
    print("TEST API GET /graph ENDPOINT")
    print("=" * 80)

    client = TestClient(app)
    response = client.get("/graph?limit=50")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert "nodes" in data
    assert "links" in data
    assert "node_count" in data
    assert "link_count" in data
    assert data["node_count"] == len(data["nodes"])
    assert data["link_count"] == len(data["links"])
    print(f"API /graph returned: {data['node_count']} nodes, {data['link_count']} links.")
    print("API GET /graph endpoint test PASSED!")


if __name__ == "__main__":
    test_graph_retriever_get_graph_data()
    print()
    test_api_graph_endpoint()
