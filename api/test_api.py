"""
Simple test script to verify the API endpoints work correctly.
Run this after starting the API server.
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health check endpoint."""
    print("Testing /health...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    print(f"✓ Health check passed: {data}")
    return True


def test_start_quiz():
    """Test starting a quiz."""
    print("\nTesting POST /start...")
    response = requests.post(f"{BASE_URL}/start")
    assert response.status_code == 200
    data = response.json()
    print(f"✓ Quiz started: session_id={data['session_id']}")
    print(f"  Question: {data['question_text'][:50]}...")
    print(f"  Top majors: {len(data['top_majors'])}")
    return data["session_id"], data["question_id"]


def test_submit_answer(session_id: str, question_id: str):
    """Test submitting an answer."""
    print(f"\nTesting POST /answer...")
    payload = {
        "session_id": session_id,
        "question_id": question_id,
        "answer": 4,  # Agree
    }
    response = requests.post(f"{BASE_URL}/answer", json=payload)
    assert response.status_code == 200
    data = response.json()
    print(f"✓ Answer submitted")
    print(f"  Questions asked: {data['questions_asked']}")
    print(f"  Entropy: {data['entropy']:.2f} bits")
    print(f"  Top probability: {data['top_probability']:.2%}")
    print(f"  Is complete: {data['is_complete']}")
    if data["question_id"]:
        print(f"  Next question: {data['question_text'][:50]}...")
    return data


def test_get_results(session_id: str):
    """Test getting results."""
    print(f"\nTesting GET /results/{session_id}...")
    response = requests.get(f"{BASE_URL}/results/{session_id}")
    assert response.status_code == 200
    data = response.json()
    print(f"✓ Results retrieved")
    print(f"  Total majors: {len(data['majors'])}")
    print(f"  Top major: {data['majors'][0]['name']} ({data['majors'][0]['probability']:.2%})")
    print(f"  Questions asked: {data['questions_asked']}")
    print(f"  Entropy history length: {len(data['entropy_history'])}")
    return data


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Stanford Major Quiz API")
    print("=" * 60)

    try:
        # Test health
        test_health()

        # Test start quiz
        session_id, question_id = test_start_quiz()

        # Test submit a few answers
        for i in range(3):
            answer_data = test_submit_answer(session_id, question_id)
            question_id = answer_data.get("question_id")
            if not question_id or answer_data["is_complete"]:
                break

        # Test get results
        test_get_results(session_id)

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to API.")
        print("  Make sure the API server is running on http://localhost:8000")
        print("  Run: uvicorn api.main:app --reload")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")


if __name__ == "__main__":
    main()
