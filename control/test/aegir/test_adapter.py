"""Test adapter class.

James Foster
"""
import pytest
import sys
from aegir.adapter import AegirAdapter

if sys.version_info[0] == 3:  # pragma: no cover
    from unittest.mock import Mock
    # from unittest import TestCase
else:                         # pragma: no cover
    from mock import Mock


@pytest.fixture(scope="class")
def dummy_aegir_adapter():
    """Test the simple test fixture used in testing the aegir adapter."""
    dummy_aegir_adapter = AegirAdapter()
    yield dummy_aegir_adapter


class TestAegirAdapter():
    """Class for testing aegir adapter behaviour."""

    def test_adapter_get(self, dummy_aegir_adapter):
        """Test the adapter get method returns the appropriate response."""
        expected_response = {'status': 'unknown'}
        mock_request = Mock()
        mock_request.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = dummy_aegir_adapter.get('status', mock_request)
        assert response.data == expected_response
        assert response.status_code == 200

    def test_adapter_get_bad_param_tree(self, dummy_aegir_adapter):
        """Test that attempting to get an inappropriate value returns an error."""
        expected_response = {'error': 'Invalid path: bad_param_tree'}
        mock_request = Mock()
        mock_request.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = dummy_aegir_adapter.get('bad_param_tree', mock_request)
        assert response.data == expected_response
        assert response.status_code == 400

    def test_cleanup(self, dummy_aegir_adapter):
        """Test the cleanup function."""
        dummy_aegir_adapter.cleanup()
        assert not dummy_aegir_adapter.controller.background_task_enable
