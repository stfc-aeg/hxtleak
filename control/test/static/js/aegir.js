let aegir_endpoint;
let task_enable_elem;

/**
 * This function is called when the DOM content of the page is loaded, and initialises
 * various elements of the sequencer page. The sequence module layout and log messages
 * are initialised from the current state of the adapter and the current execution state
 * is retrieved and managed appropriately.
 */
document.addEventListener("DOMContentLoaded", function () {

    // Initialise the adapter endpoint
    aegir_endpoint = new AdapterEndpoint("aegir");

    task_enable_elem = document.querySelector('#task-enable');

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
        var ioloop_task_count = result.background_task.ioloop_count;
        var thread_task_count = result.background_task.thread_count;
        var task_enabled = result.background_task.enable;

        document.querySelector("#task-count").innerHTML = 
            `ioloop: ${ioloop_task_count} thread: ${thread_task_count}`;
        task_enable_elem.checked = task_enabled;
    })
    .catch(error => {
        console.log(error.message);
    });
}

function change_enable() {
    var enabled = task_enable_elem.checked;
    console.log("Background task enable changed to " + (enabled ? "true" : "false"));
    aegir_endpoint.put({'enable': enabled}, 'background_task')
    .then(result => {
        // console.log(result);
    })
    .catch(error => {
        console.log(error.message);
    });
}
