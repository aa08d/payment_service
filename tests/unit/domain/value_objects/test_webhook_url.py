from dataclasses import FrozenInstanceError

import pytest

from payment.domain.common.exceptions import DomainError
from payment.domain.payment.value_objects import WebhookURL
from payment.domain.payment.value_objects.webhook_url import InvalidWebhookURLError, WebhookURLError


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com",
        "https://example.com",
        "https://example.com/path/to/hook?token=abc&x=1#fragment",
        "https://example.com:8443/hook",
        "http://localhost:8000/hook",
        "http://127.0.0.1:1",
        "http://example.com:65535",
        "http://[::1]:8080/hook",
        "https://webhook.site/6f1b7a0e-0000-4000-8000-000000000000",
        "HTTPS://EXAMPLE.COM/Hook",
    ],
)
def test_webhook_url_accepts_http_and_https_urls(url: str) -> None:
    assert WebhookURL(url).value == url


@pytest.mark.parametrize(
    "url",
    [
        "",
        " ",
        "example.com",
        "//example.com/hook",
        "ftp://example.com/hook",
        "file:///etc/passwd",
        "javascript:alert(1)",
        "http://",
        "https:///hook",
        "http://:80",
        "http://exa mple.com",
        " https://example.com",
        "https://example.com ",
        "https://example.com/\nhook",
    ],
)
def test_webhook_url_rejects_not_http_urls_without_host_or_with_whitespace(url: str) -> None:
    with pytest.raises(InvalidWebhookURLError):
        WebhookURL(url)


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com:0",
        "http://example.com:65536",
        "http://example.com:99999",
        "http://example.com:abc",
        "http://example.com:",
    ],
)
def test_webhook_url_rejects_invalid_port(url: str) -> None:
    with pytest.raises(InvalidWebhookURLError):
        WebhookURL(url)


def test_webhook_url_error_contains_rejected_url() -> None:
    with pytest.raises(InvalidWebhookURLError) as exc_info:
        WebhookURL("ftp://example.com")

    assert exc_info.value.url == "ftp://example.com"
    assert "ftp://example.com" in exc_info.value.message
    assert isinstance(exc_info.value, WebhookURLError)
    assert isinstance(exc_info.value, DomainError)


def test_webhook_url_equality_depends_on_value() -> None:
    assert WebhookURL("https://example.com") == WebhookURL("https://example.com")
    assert WebhookURL("https://example.com") != WebhookURL("https://example.org")


def test_webhook_url_is_immutable() -> None:
    url = WebhookURL("https://example.com")

    with pytest.raises(FrozenInstanceError):
        url.value = "https://example.org"  # type: ignore[misc]
