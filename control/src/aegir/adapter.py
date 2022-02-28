"""Skeleton adaptor for AEGIR project.


"""
import logging
import tornado
import time
from concurrent import futures

from tornado.ioloop import PeriodicCallback
from tornado.concurrent import run_on_executor
from tornado.escape import json_decode

from odin.adapters.adapter import ApiAdapter, ApiAdapterResponse, request_types, response_types
from odin.adapters.parameter_tree import ParameterTree, ParameterTreeError
from odin._version import get_versions

class AegirAdapter(ApiAdapter):

    def __init__(self, **kwargs):
        """Initialise the adapter object.

        :param kwargs: keyawrd argument list that is passed to superclass
                       init method to populate options dictionary
        """
        # Initalise super class
        super().__init__(**kwargs)

        # Parse options
        background_task_enable = bool(self.options.get('background_task_enable', False))
        background_task_interval = float(self.options.get('background_task_interval', 1.0))

        self.controller = AegirController(background_task_enable, background_task_interval)

        logging.debug("AegirAdapter loaded")

    def initialize(self, adapters):
        """Initialize internal list of registered adapters.

        This method, if present, is called by odin-control once all adapters have been loaded. It
        passes a dict of loaded adapters to facilitate inter-adapter communication.

        :param adapters: dictionary of currently loaded adapters
        """
        self.controller.initialize(adapters)

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
        except ParameterTreeError as e:
            response = {'error': str(e)}
            status_code = 400

        content_type = 'application/json'

        return ApiAdapterResponse(response, content_type=content_type,
                                  status_code=status_code)

    @request_types('application/json')
    @response_types('application/json', default='application/json')
    def put(self, path, request):
        """Handle an HTTP PUT request.

        This method handles an HTTP PUT request, returning a JSON response.

        :param path: URI path of request
        :param request: HTTP request object
        :return: an ApiAdapterResponse object containing the appropriate response
        """

        content_type = 'application/json'

        try:
            data = json_decode(request.body)
            self.controller.set(path, data)
            response = self.controller.get(path)
            status_code = 200
        except AegirControllerError as e:
            response = {'error': str(e)}
            status_code = 400
        except (TypeError, ValueError) as e:
            response = {'error': 'Failed to decode PUT request body: {}'.format(str(e))}
            status_code = 400

        logging.debug(response)

        return ApiAdapterResponse(response, content_type=content_type,
                                  status_code=status_code)

    def delete(self, path, request):
        """Handle an HTTP DELETE request.

        This method handles an HTTP DELETE request, returning a JSON response.

        :param path: URI path of request
        :param request: HTTP request object
        :return: an ApiAdapterResponse object containing the appropriate response
        """
        logging.debug('DELETE on path %s from %s: method not implemented by %s',
                        path, request.remote_ip, self.name)
        response = "DELETE method not implemented by {}".format(self.name)
        return ApiAdapterResponse(response, status_code=400)


class AegirControllerError(Exception):
    """Simple exception class to wrap lower-level exceptions."""

    pass

class AegirController():

    # Thread executor used for background tasks
    executor = futures.ThreadPoolExecutor(max_workers=1)

    def __init__(self, background_task_enable, background_task_interval):
        """Initialise the controller object.

        This constructor initialises the controller object, building a parameter tree and
        launching a background task if enabled
        """
        # Save arguments
        self.background_task_enable = background_task_enable
        self.background_task_interval = background_task_interval

        # Store initialisation time
        self.init_time = time.time()

        # Get package version information
        version_info = get_versions()

        # Set the background task counters to zero
        self.background_ioloop_counter = 0
        self.background_thread_counter = 0

        # Build a parameter tree for the background task
        bg_task = ParameterTree({
            'ioloop_count': (lambda: self.background_ioloop_counter, None),
            'thread_count': (lambda: self.background_thread_counter, None),
            'enable': (lambda: self.background_task_enable, self.set_task_enable),
            'interval': (lambda: self.background_task_interval, self.set_task_interval),
        })

        # Store all information in a parameter tree
        self.param_tree = ParameterTree({
            'odin_version': version_info['version'],
            'tornado_version': tornado.version,
            'server_uptime': (self.get_server_uptime, None),
            'background_task': bg_task 
        })

        # Launch the background task if enabled in options
        if self.background_task_enable:
            self.start_background_tasks()

    def initialize(self, adapters):
        pass

    def get_server_uptime(self):
        """Get the uptime for the ODIN server.

        This method returns the current uptime for the ODIN server.
        """
        return time.time() - self.init_time

    def get(self, path):
        """Get the parameter tree.

        This method returns the parameter tree for use by clients via the Workshop adapter.

        :param path: path to retrieve from tree
        """
        return self.param_tree.get(path)

    def set(self, path, data):
        """Set parameters in the parameter tree.

        This method simply wraps underlying ParameterTree method so that an exceptions can be
        re-raised with an appropriate WorkshopError.

        :param path: path of parameter tree to set values for
        :param data: dictionary of new data values to set in the parameter tree
        """
        try:
            self.param_tree.set(path, data)
        except ParameterTreeError as e:
            raise AegirControllerError(e)

    def cleanup(self):
        """Clean up the Workshop instance.

        This method stops the background tasks, allowing the adapter state to be cleaned up
        correctly.
        """
        self.stop_background_tasks()

    def set_task_interval(self, interval):
        """Set the background task interval."""
        logging.debug("Setting background task interval to %f", interval)
        self.background_task_interval = float(interval)
        
    def set_task_enable(self, enable):
        """Set the background task enable."""
        enable = bool(enable)

        if enable != self.background_task_enable:
            if enable:
                self.start_background_tasks()
            else:
                self.stop_background_tasks()

    def start_background_tasks(self):
        """Start the background tasks."""
        logging.debug(
            "Launching background tasks with interval %.2f secs", self.background_task_interval
        )

        self.background_task_enable = True

        # Register a periodic callback for the ioloop task and start it
        self.background_ioloop_task = PeriodicCallback(
            self.background_ioloop_callback, self.background_task_interval * 1000
        )
        self.background_ioloop_task.start()

        # Run the background thread task in the thread execution pool
        self.background_thread_task()

    def stop_background_tasks(self):
        """Stop the background tasks."""
        self.background_task_enable = False
        self.background_ioloop_task.stop()

    def background_ioloop_callback(self):
        """Run the adapter background IOLoop callback.

        This simply increments the background counter before returning. It is called repeatedly
        by the periodic callback on the IOLoop.
        """

        if self.background_ioloop_counter < 10 or self.background_ioloop_counter % 20 == 0:
            logging.debug(
                "Background IOLoop task running, count = %d", self.background_ioloop_counter
            )

        self.background_ioloop_counter += 1

    @run_on_executor
    def background_thread_task(self):
        """Run the adapter background thread task.

        This method runs in the thread executor pool, sleeping for the specified interval and 
        incrementing its counter once per loop, until the background task enable is set to false.
        """

        sleep_interval = self.background_task_interval

        while self.background_task_enable:
            time.sleep(sleep_interval)
            if self.background_thread_counter < 10 or self.background_thread_counter % 20 == 0:
                logging.debug(
                    "Background thread task running, count = %d", self.background_thread_counter
                )
            if self.background_task_enable:
                self.background_thread_counter += 1

        logging.debug("Background thread task stopping")

