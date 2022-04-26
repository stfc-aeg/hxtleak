let aegir_endpoint;

/**
 * This function is called when the DOM content of the page is loaded, and initialises
 * various elements of the sequencer page. The sequence module layout and log messages
 * are initialised from the current state of the adapter and the current execution state
 * is retrieved and managed appropriately.
 */
document.addEventListener("DOMContentLoaded", function () {

    // Initialise the adapter endpoint
    aegir_endpoint = new AdapterEndpoint("aegir");

    update_api_version();
    update_api_info();
    poll_update();
});

function update_api_version()
{
    document.querySelector('#api-version').innerHTML = aegir_endpoint.api_version;
}

function update_api_info()
{
    aegir_endpoint.get_adapters()
    .then(result => {
        adapter_list = result.adapters.join(", ")
        document.querySelector('#api-adapters').innerHTML = adapter_list;
    })
    .catch(error => {
        console.log(error.message);
    });
}

function poll_update() 
{
    update_background_task();
    setTimeout(poll_update, 500);
}

function update_background_task()
{
    aegir_endpoint.get('')
    .then(result => {
        var task_arduino_status = result.arduino_status;
        var task_time_received = result.time_received;

        document.querySelector("#arduino-stat").innerHTML = 
            `${task_arduino_status}`;
        document.querySelector("#time-receive").innerHTML =
            `${task_time_received}`;
    })
    .catch(error => {
        console.log(error.message);
    });
}
