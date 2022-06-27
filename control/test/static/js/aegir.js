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
    init();

    update_api_version();
    update_api_info();
    poll_update();

    poll_chart_update();
});

function init()
{
    init_environment_tracking();
}

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

function poll_chart_update()
{
    update_chart_temps();
    setTimeout(poll_chart_update, 4000);
}

function set_chart_animation_duration(duration) {
    chart_temp.options.animation.duration = duration
    chart_hum.options.animation.duration = duration

    const d = new Date();
    exdays = 30;    // Keep this cookie for 30 days
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    let expires = "expires="+d.toUTCString();
    document.cookie = "chartAnimationDuration="+duration.toString()+";"+expires+";path=/;SameSite=Strict;";
}

function get_chart_animation_duration() {
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    let name = "chartAnimationDuration=";
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
		while (c.charAt(0) == ' ') {
          c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
          return parseInt(c.substring(name.length, c.length));
        }
    }
    return 1000;  // Default duration if no cookie is found
}

var chart_temp;
var chart_hum;
function init_environment_tracking() {
    var chart_element = document.getElementById("temperature-chart").getContext('2d');
    chart_temp = new Chart(chart_element,
    {
        type: 'line',
        yAxisID: 'Temperature /C',
        data: {
            labels: environment_tracking_time,
            datasets: [{
                label: "Room",
                data: environment_tracking_data_case_temp,
                backgroundColor: ['rgba(255, 0, 0, .2)'],
                }
            ]
        },
        options: {
            animation: {
                duration: get_chart_animation_duration(),
            },
            responsiveAnimationDuration: 0,
            elements: {
                line: {
                    tension: 0
                    }
            },
	    scales: {
	        xAxes: [{
                    type: 'time',
		    distribution: 'linear',
		    ticks: {
	                source: 'data',
		    }
		}]
	    }
        }
    });

    var chart_element = document.getElementById("humidity-chart").getContext('2d');
    chart_hum = new Chart(chart_element,
    {
        type: 'line',
        yAxisID: 'Relative Humidity /%',
        data: {
            labels: environment_tracking_time,
            datasets: [{
                label: "Room",
                data: environment_tracking_data_case_humidity,
                backgroundColor: ['rgba(0, 0, 255, .2)'],
                }
            ]
        },
        options: {
            animation: {
                duration: get_chart_animation_duration(),
            },
            responsive: true,
            responsiveAnimationDuration: 0,
            elements: {
                line: {
                    tension: 0
                    }
            },
	    scales: {
	        xAxes: [{
                    type: 'time',
            animation: {
                duration: get_chart_animation_duration(),
            },
		    distribution: 'linear',
			ticks: {
	                source: 'data',
		    }
		}]
	    }
        }
    });
}

var environment_tracking_data_case_temp = [];
var environment_tracking_data_case_humidity = [];
var environment_tracking_time = [];
var environment_tracking_valuelimit = 40;
var temp_ambient = NaN;
var hum_ambient = NaN;
function update_chart_temps() {

    aegir_endpoint.get('')
    .then(result => {
        temp_ambient = result.packet_info.temp.toFixed(2);
        hum_ambient = result.packet_info.humidity.toFixed(2);
        $('#temp-ambient').html(temp_ambient);
        $('#hum-ambient').html(hum_ambient);
    })
    .catch(error => {
        console.log(error.message);
    });

    environment_tracking_data_case_temp.push(temp_ambient);
    if (environment_tracking_data_case_temp.length > environment_tracking_valuelimit) environment_tracking_data_case_temp.shift();

    environment_tracking_data_case_humidity.push(hum_ambient);
    if (environment_tracking_data_case_humidity.length > environment_tracking_valuelimit) environment_tracking_data_case_humidity.shift();

    dt = new Date();
    environment_tracking_time.push(
    dt.toISOString()
    );
    if (environment_tracking_time.length > environment_tracking_valuelimit) environment_tracking_time.shift();

    chart_temp.update();
    chart_hum.update();
}

function update_background_task()
{
    aegir_endpoint.get('')
    .then(result => {
        var task_status = result.status;

        var task_packet_temp = result.packet_info.temp;
        var task_packet_humidity = result.packet_info.humidity;
        var task_packet_fault = result.packet_info.fault;
        var task_packet_checksum = result.packet_info.checksum;
        var task_packet_eop = result.packet_info.eop;

        var task_good_packets = result.good_packets;
        var task_bad_packets = result.bad_packets;

        var task_time_received = result.time_received;

        document.querySelector("#status").innerHTML = 
            `${task_status}`;

        document.querySelector("#packet-temp").innerHTML = 
            `${task_packet_temp.toFixed(2)}`;
        document.querySelector("#packet-humidity").innerHTML = 
            `${task_packet_humidity.toFixed(2)}`;
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
