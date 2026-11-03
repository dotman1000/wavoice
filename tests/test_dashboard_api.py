"""Tests for the authenticated assistant profile dashboard API."""

from fastapi.testclient import TestClient

from wavoice.core.config import Settings
from wavoice.server.app import create_app, load_assistant_profile


def make_client(token: str | None = "test-dashboard-token", profile_file: str = "data/assistant-profile.json") -> TestClient:
    config_values = {"WAVOICE_ASSISTANT_PROFILE_FILE": profile_file}
    if token is not None:
        config_values["WAVOICE_DASHBOARD_TOKEN"] = token
    return TestClient(create_app(config=Settings(**config_values)))


def test_dashboard_page_is_served(tmp_path):
    client = make_client(profile_file=str(tmp_path / "profile.json"))

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "Assistant profile" in response.text or "assistant" in response.text.lower()


def test_profile_api_is_disabled_without_dashboard_token(tmp_path):
    client = make_client(token=None, profile_file=str(tmp_path / "profile.json"))

    response = client.get("/api/assistant-profile")

    assert response.status_code == 503


def test_profile_api_rejects_missing_or_invalid_bearer_token(tmp_path):
    client = make_client(profile_file=str(tmp_path / "profile.json"))

    assert client.get("/api/assistant-profile").status_code == 401
    assert client.get(
        "/api/assistant-profile",
        headers={"Authorization": "Bearer wrong-token"},
    ).status_code == 401


def test_profile_api_reads_only_assistant_profile_fields(tmp_path):
    client = make_client(profile_file=str(tmp_path / "profile.json"))

    response = client.get(
        "/api/assistant-profile",
        headers={"Authorization": "Bearer test-dashboard-token"},
    )

    assert response.status_code == 200
    assert response.json()["assistant_name"] == "My WhatsApp Assistant"
    assert "whatsapp_token" not in response.json()
    assert "gemini_api_key" not in response.json()


def test_profile_api_updates_allowlisted_fields_for_new_calls(tmp_path):
    profile_file = tmp_path / "profile.json"
    client = make_client(profile_file=str(profile_file))
    headers = {"Authorization": "Bearer test-dashboard-token"}
    profile = {
        "assistant_name": "Reception Assistant",
        "assistant_greeting": "Hello, how can I help?",
        "assistant_role": "Answer approved questions clearly.",
        "assistant_knowledge": "Opening hours: Monday to Friday.",
        "assistant_rules": "Do not guess.",
        "assistant_language": "auto",
        "assistant_voice": "Kore",
        "assistant_style": "Calm and professional",
        "assistant_handover": "Offer a human callback for complaints.",
    }

    saved = client.put("/api/assistant-profile", headers=headers, json=profile)

    assert saved.status_code == 200
    assert saved.json()["status"] == "saved"
    loaded = client.get("/api/assistant-profile", headers=headers)

    assert loaded.status_code == 200
    assert loaded.json() == profile
    assert profile_file.exists()
    restarted_client = make_client(profile_file=str(profile_file))
    restarted = restarted_client.get("/api/assistant-profile", headers=headers)
    assert restarted.status_code == 200
    assert restarted.json() == profile


def test_profile_api_rejects_oversized_profile_fields(tmp_path):
    client = make_client(profile_file=str(tmp_path / "profile.json"))
    headers = {"Authorization": "Bearer test-dashboard-token"}
    profile = {
        "assistant_name": "x" * 61,
        "assistant_greeting": "Hello",
        "assistant_role": "Role",
        "assistant_knowledge": "",
        "assistant_rules": "Rules",
        "assistant_language": "auto",
        "assistant_voice": "Puck",
        "assistant_style": "Natural",
        "assistant_handover": "Callback",
    }

    response = client.put("/api/assistant-profile", headers=headers, json=profile)

    assert response.status_code == 422



def test_saved_profile_loader_overlays_environment_defaults(tmp_path):
    profile_file = tmp_path / "profile.json"
    client = make_client(profile_file=str(profile_file))
    headers = {"Authorization": "Bearer test-dashboard-token"}
    profile = {
        "assistant_name": "Persisted Reception",
        "assistant_greeting": "Welcome back.",
        "assistant_role": "Answer reception questions.",
        "assistant_knowledge": "Office opens at nine.",
        "assistant_rules": "Do not guess.",
        "assistant_language": "auto",
        "assistant_voice": "Kore",
        "assistant_style": "Calm",
        "assistant_handover": "Offer a staff callback.",
    }
    assert client.put("/api/assistant-profile", headers=headers, json=profile).status_code == 200

    restarted_config = Settings(**{"WAVOICE_ASSISTANT_PROFILE_FILE": str(profile_file)})
    load_assistant_profile(restarted_config)

    assert restarted_config.assistant_name == "Persisted Reception"
    assert restarted_config.assistant_voice == "Kore"
