"""Main adapter portion of the Aegir Adapter.

This class initialises the adapter which sets the port name and creates
the controller object, and handles HTTP GET requests to the adapter.

James Foster
"""
import logging

from odin.adapters.adapter import ApiAdapter, ApiAdapterResponse, request_types, response_types
from odin.adapters.parameter_tree import ParameterTreeError
from odin.util import decode_request_body

from aegir.controller import AegirController
from aegir.util import AegirError

class AegirAdapter(ApiAdapter):
    """Main adapter class for the Aegir Adapter."""

    def __init__(self, **kwargs):
        """Initialise the adapter object.

        :param kwargs: keyword argument list that is passed to superclass
                       init method to populate options dictionary
        """
        # Initalise super class
        super().__init__(**kwargs)

        # Parse options
        port_name = str(self.options.get('port_name', '/dev/ttyACM0'))

        self.controller = AegirController(port_name)

        logging.debug("AegirAdapter loaded")

    @response_types('application/json', default='application/json')
    def get(self, path, request):
        """Handle an HTTP GET request.

        This method handles an HTTP GET request, returning a JSON response.

        :param path: URI path of request
        :param request: HTTP request object
        :return: an ApiAdapterResponse object containing the appropriate response
        """
        try:
            response = self.controller.get(path)
            status_code = 200
        except (ParameterTreeError, AegirError) as e:
            response = {'error': str(e)}
            status_code = 400

        content_type = 'application/json'

        return ApiAdapterResponse(response, content_type=content_type,
                                  status_code=status_code)

    @request_types('application/json', 'application/vnd.odin-native')
    @response_types('application/json', default='application/json')
    def put(self, path, request):
        """Handle an HTTP PUT request.
        This method handles an HTTP PUT request, decoding the request and attempting to set values
        in the asynchronous parameter tree as appropriate.
        :param path: URI path of request
        :param request: HTTP request object
        :return: an ApiAdapterResponse object containing the appropriate response
        """
        content_type = 'application/json'

        try:
            data = decode_request_body(request)
            response = self.controller.set(path, data)
            status_code = 200
        except (ParameterTreeError, AegirError) as e:
            response = {'error': str(e)}
            status_code = 400

        return ApiAdapterResponse(
            response, content_type=content_type, status_code=status_code
        )

    def cleanup(self):
        """Clean up the adapter.

        This method stops the background tasks, allowing the adapter state to be cleaned up
        correctly.
        """
        logging.debug("Cleanup called")
        self.controller.cleanup()
