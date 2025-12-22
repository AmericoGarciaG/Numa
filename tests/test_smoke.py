"""Smoke tests for Numa Nexus Protocol."""

import sys
import os
import pytest
from unittest.mock import MagicMock

# Ensure src is in pythonpath
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Force credentials path for tests if file exists
creds_path = os.path.abspath("credentials.json")
if os.path.exists(creds_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path

def test_project_structure():
    """Verify critical directories exist."""
    assert os.path.exists("src"), "src/ directory missing"
    assert os.path.exists("src/modules"), "src/modules/ directory missing"
    assert os.path.exists("src/core"), "src/core/ directory missing"
    assert os.path.exists("docs/LOGIC.md"), "docs/LOGIC.md missing"
    assert os.path.exists("GOVERNANCE.md"), "GOVERNANCE.md missing"
    assert os.path.exists("credentials.json"), "credentials.json missing"

def test_imports_finance_core():
    """Verify Finance Core module imports."""
    from src.modules.finance_core import service, models, schemas
    assert service is not None
    assert models is not None
    assert schemas is not None

def test_imports_api_gateway():
    """Verify API Gateway module imports."""
    from src.modules.api_gateway import router, service
    assert router is not None
    assert service is not None

def test_imports_ai_brain():
    """Verify AI Brain module imports."""
    # Mock google libraries if they are not yet installed or configured
    # But since we are running this AFTER pip install, they should be there.
    # However, to be safe against credential errors during import (some libs check on import):
    try:
        from src.modules.ai_brain import service, transcriber, reasoning, connector
        assert service is not None
        assert transcriber is not None
        assert reasoning is not None
        assert connector is not None
    except ImportError as e:
        pytest.fail(f"Failed to import AI Brain modules: {e}")
    except Exception as e:
        # Some Google libs might error on import if creds are bad? usually not on import.
        pytest.fail(f"Error importing AI Brain modules: {e}")

def test_transcriber_structure():
    """Verify Transcriber class structure."""
    from src.modules.ai_brain.transcriber import Transcriber
    assert hasattr(Transcriber, "transcribe")

def test_reasoning_structure():
    """Verify GeminiReasoning class structure."""
    from src.modules.ai_brain.reasoning import GeminiReasoning
    assert hasattr(GeminiReasoning, "extract_transaction_data")
