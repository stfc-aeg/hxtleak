from ast import Import
import pytest
import sys
from aegir.adapter import AegirAdapter
from aegir.controller import AegirControllerError

from odin.adapters.dummy import DummyAdapter
from odin.adapters.parameter_tree import ParameterAccessor, ParameterTree, ParameterTreeError
from odin.adapters.adapter import ApiAdapter, ApiAdapterRequest, ApiAdapterResponse, request_types, response_types
from odin._version import get_versions
from copy import deepcopy

if sys.version_info[0] == 3:  # pragma: no cover
    from unittest.mock import Mock
    # from unittest import TestCase
else:                         # pragma: no cover
    from mock import Mock

class DummyAdapterTestFixture(object):
    """Container class used in fixtures for testing the DummyAdapter."""

    def __init__(self):

        self.adapter = DummyAdapter(background_task_enable=True)
        self.path = '/dummy/path'
        self.request = Mock()
        self.request.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

@pytest.fixture(scope="class")
def test_dummy_adapter():
    """Simple test fixture for testing the dummy adapter."""
    test_dummy_adapter = DummyAdapterTestFixture()
    yield test_dummy_adapter

@pytest.fixture(scope="class")
def dummy_aegir_adapter():
    dummy_aegir_adapter = AegirAdapter()
    yield dummy_aegir_adapter

class TestAegirAdapter():
    def test_adapter_get(self, dummy_aegir_adapter):
        expected_response = {'odin_version': '1.1.0'}
        mock_request = Mock()
        mock_request.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = dummy_aegir_adapter.get('odin_version', mock_request)
        assert response.data == expected_response
        assert response.status_code == 200
    
    def test_adapter_get_bad_param_tree(self, dummy_aegir_adapter):
        expected_response = {'error': 'Invalid path: bad_param_tree'}
        mock_request = Mock()
        mock_request.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = dummy_aegir_adapter.get('bad_param_tree', mock_request)
        assert response.data == expected_response
        assert response.status_code == 400
    
    def test_cleanup(self, dummy_aegir_adapter):
        dummy_aegir_adapter.cleanup()
        assert dummy_aegir_adapter.controller.background_task_enable == False

class TestDummyAdapter():

    def test_dummy(self):
        '''
        Dummy test to verify pytest setup
        '''
        assert True

    def test_adapter_get(self, test_dummy_adapter):
        """Test that a call to the GET method of the dummy adapter returns the correct response."""
        expected_response = {
            'response': 'DummyAdapter: GET on path {}'.format(test_dummy_adapter.path)
            }
        response = test_dummy_adapter.adapter.get(test_dummy_adapter.path, 
            test_dummy_adapter.request)
        assert response.data == expected_response
        assert response.status_code == 200

    def test_adapter_put(self, test_dummy_adapter):
        """Test that a call to the PUT method of the dummy adapter returns the correct response."""
        expected_response = {
            'response': 'DummyAdapter: PUT on path {}'.format(test_dummy_adapter.path)
            }
        response = test_dummy_adapter.adapter.put(test_dummy_adapter.path,
            test_dummy_adapter.request)
        assert response.data == expected_response
        assert response.status_code == 200

    def test_adapter_delete(self, test_dummy_adapter):
        """Test that a call to the DELETE method of the dummy adapter returns the correct response."""
        response = test_dummy_adapter.adapter.delete(test_dummy_adapter.path, 
            test_dummy_adapter.request)
        assert response.data == 'DummyAdapter: DELETE on path {}'.format(test_dummy_adapter.path)
        assert response.status_code == 200

    def test_adapter_put_bad_content_type(self, test_dummy_adapter):
        """
        Test that a call to the dummy adapter with an incorrect content type generates the
        appropriate error response.
        """
        bad_request = Mock()
        bad_request.headers = {'Content-Type': 'text/plain'}
        response = test_dummy_adapter.adapter.put(test_dummy_adapter.path, bad_request)
        assert response.data == 'Request content type (text/plain) not supported'
        assert response.status_code == 415

    def test_adapter_put_bad_accept_type(self, test_dummy_adapter):
        """
        Test that a call to the dummy adapter with an incorrect accept type generates the
        appropriate error response.
        """
        bad_request = Mock()
        bad_request.headers = {'Accept': 'text/plain'}
        response = test_dummy_adapter.adapter.put(test_dummy_adapter.path, bad_request)
        assert response.data == 'Requested content types not supported'
        assert response.status_code == 406

    def test_adapter_cleanup(self, test_dummy_adapter):
        """
        Test that a call the dummy adapter cleanup method cleans up correctly.
        """
        test_dummy_adapter.adapter.background_task_counter = 1000
        test_dummy_adapter.adapter.cleanup()
        assert test_dummy_adapter.adapter.background_task_counter == 0