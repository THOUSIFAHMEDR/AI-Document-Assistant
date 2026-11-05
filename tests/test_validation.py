import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app

def test_backend_validations():
    client = TestClient(app)

    # 1. Health
    r = client.get('/health')
    assert r.status_code == 200 and r.json()['status'] == 'healthy'

    # 2. Documents
    r = client.get('/documents')
    assert r.status_code == 200
    docs = r.json().get('documents', [])
    assert len(docs) >= 1
    print('Found stored documents:', len(docs))

    # 3. PDF retrieval
    doc_id = docs[0]['document_id']
    r = client.get(f'/documents/{doc_id}/pdf')
    assert r.status_code == 200
    assert len(r.content) > 1000

    # 4. Empty question rejection
    r = client.post('/ask', json={'document_id': doc_id, 'question': '   '})
    assert r.status_code == 400

    # 5. Invalid file rejection
    r = client.post('/upload', files={'file': ('test.txt', b'hello', 'text/plain')})
    assert r.status_code == 400

    print('SUCCESS: All backend validation checks passed!')

if __name__ == '__main__':
    test_backend_validations()
