import os
import sys
import base64
import pytest
from PIL import Image

# Ensure project root in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.styles import BANNER_PATH, LOGO_PATH, get_banner_base64, get_logo_base64, render_brand_header


def test_banner_file_exists_and_valid():
    """Verify that the new brand banner asset exists, is non-empty, and has expected dimensions."""
    assert os.path.exists(BANNER_PATH), f"Banner file not found at {BANNER_PATH}"
    file_size = os.path.getsize(BANNER_PATH)
    assert file_size > 10000, f"Banner file size suspiciously small: {file_size} bytes"

    # Verify PIL can open and validate dimensions
    with Image.open(BANNER_PATH) as img:
        assert img.format == "PNG"
        width, height = img.size
        assert width >= 800, f"Expected banner width >= 800, got {width}"
        assert height >= 200, f"Expected banner height >= 200, got {height}"
        # Aspect ratio should be roughly wide banner (~3.0 to ~3.8)
        aspect = width / height
        assert 2.5 <= aspect <= 4.5, f"Expected wide banner aspect ratio, got {aspect}"


def test_banner_base64_generation():
    """Verify that get_banner_base64 correctly converts banner into valid base64 string."""
    b64_str = get_banner_base64()
    assert isinstance(b64_str, str)
    assert len(b64_str) > 1000, "Base64 banner string is unexpectedly short"

    # Decode and verify header matches PNG magic bytes
    decoded = base64.b64decode(b64_str)
    assert decoded[:8] == b"\x89PNG\r\n\x1a\n", "Decoded base64 does not match PNG signature"


def test_logo_asset_integrity():
    """Verify that the brand logo file exists and generates base64."""
    assert os.path.exists(LOGO_PATH)
    logo_b64 = get_logo_base64()
    assert len(logo_b64) > 100


def test_brand_header_rendering(monkeypatch):
    """Verify render_brand_header produces expected HTML markup with the new banner."""
    rendered_markdowns = []

    def mock_markdown(body, unsafe_allow_html=False):
        rendered_markdowns.append(body)

    import streamlit as st
    monkeypatch.setattr(st, "markdown", mock_markdown)

    render_brand_header()
    assert len(rendered_markdowns) == 1
    content = rendered_markdowns[0]

    # Verify it references the new banner container and tagline alt text
    assert "brand-hero-banner" in content
    assert "Free care. No insurance. Know where to go." in content
    assert "data:image/png;base64," in content


def test_brand_header_fallback_rendering(monkeypatch):
    """Verify fallback rendering when banner image is unavailable."""
    rendered_markdowns = []

    def mock_markdown(body, unsafe_allow_html=False):
        rendered_markdowns.append(body)

    import streamlit as st
    monkeypatch.setattr(st, "markdown", mock_markdown)
    import utils.styles as styles_mod
    monkeypatch.setattr(styles_mod, "get_banner_base64", lambda: "")

    render_brand_header()
    assert len(rendered_markdowns) == 1
    content = rendered_markdowns[0]

    # Verify fallback markup matches the new identity
    assert "brand-hero" in content
    assert "Free care. No insurance. Know where to go." in content
    assert "CareAt" in content
    assert "Zero" in content
