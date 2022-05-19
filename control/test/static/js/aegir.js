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

        var task_packet_t1 = result.packet_info.t1;
        var task_packet_t2 = result.packet_info.t2;
        var task_packet_fault = result.packet_info.fault;
        var task_packet_checksum = result.packet_info.checksum;
        var task_packet_eop = result.packet_info.eop;

        var task_good_packets = result.good_packets;
        var task_bad_packets = result.bad_packets;

        var task_time_received = result.time_received;

        document.querySelector("#arduino-stat").innerHTML = 
            `${task_arduino_status}`;

        document.querySelector("#packet-t1").innerHTML = 
            `${task_packet_t1}`;
        document.querySelector("#packet-t2").innerHTML = 
            `${task_packet_t2}`;
        document.querySelector("#packet-fault").innerHTML = 
            `${task_packet_fault}`;
        document.querySelector("#packet-checksum").innerHTML = 
            `${task_packet_checksum}`;
        document.querySelector("#packet-eop").innerHTML = 
            `${task_packet_eop}`;

        document.querySelector("#good-packets").innerHTML = 
            `${task_good_packets}`;
        document.querySelector("#bad-packets").innerHTML = 
            `${task_bad_packets}`;

        document.querySelector("#time-receive").innerHTML =
            `${task_time_received}`;
    })
    .catch(error => {
        console.log(error.message);
    });
}
