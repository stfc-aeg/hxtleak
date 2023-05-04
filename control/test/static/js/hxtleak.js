let hxtleak_endpoint;

/**
 * This function is called when the DOM content of the page is loaded, and initialises
 * various elements of the sequencer page. The sequence module layout and log messages
 * are initialised from the current state of the adapter and the current execution state
 * is retrieved and managed appropriately.
 */
document.addEventListener("DOMContentLoaded", function () {

    // Initialise the adapter endpoint
    hxtleak_endpoint = new AdapterEndpoint("hxtleak");
    init();
    poll_update();
    poll_chart_update();
});

function init()
{
    // Initialise the charts
    init_environment_tracking();
}

function poll_update() 
{
    // Update the data on the page
    update_background_task();
    update_failed_packet_notif();
    update_fault_det_notif();
    setTimeout(poll_update, 500);
}

function poll_chart_update()
{
    // Update the chart information
    update_chart_temps();
    setTimeout(poll_chart_update, get_chart_update_speed());
}

function set_chart_animation_duration(duration) 
{
    // A cookie which sets the speed of chart animation.
    chart_temp.options.animation.duration = duration
    chart_hum.options.animation.duration = duration

    const d = new Date();
    exdays = 30;    // Keep this cookie for 30 days
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    let expires = "expires="+d.toUTCString();
    document.cookie = "chartAnimationDuration="+duration.toString()+";"+expires+";path=/;SameSite=Strict;";
}

function get_chart_animation_duration() 
{
    // Retrieves the chart animation duration cookie.
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

function set_chart_update_speed(speed) 
{
    // A cookie which sets the speed of chart update.
    const d = new Date();
    exdays = 30;    // Keep this cookie for 30 days
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    let expires = "expires="+d.toUTCString();
    document.cookie = "chartUpdateSpeed="+speed.toString()+";"+expires+";path=/;SameSite=Strict;";
}

function get_chart_update_speed()
{
    // Retrieves the chart update speed cookie.
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    let name = "chartUpdateSpeed=";
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
		while (c.charAt(0) == ' ') {
          c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
          return parseInt(c.substring(name.length, c.length));
        }
    }
    return 4000;  // Default duration if no cookie is found
}

function toggle_chart_speed()
{
    // Toggles chart speed between fast and slow.
    var current_speed = get_chart_update_speed();
    if (current_speed == 4000) {
        set_chart_update_speed(2000);
        set_chart_animation_duration(500);
    } else {
        set_chart_update_speed(4000);
        set_chart_animation_duration(1000);
    }
}

var chart_temp;
var chart_hum;
function init_environment_tracking() 
{
    // Builds the charts with the relevant information.
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
                }],
                yAxes: [{
                    ticks: {
                        min: -5,
                        max: 50,
                        stepSize: 5,
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
                }],
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        min: 0,
                        max: 100,
                        stepSize: 10,
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
function update_chart_temps() 
{
    // Updates the information on the charts.
    hxtleak_endpoint.get('')
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

var task_bad_packets = NaN
var task_packet_fault = NaN
function update_background_task()
{
    // Updates the information for the text boxes.
    hxtleak_endpoint.get('')
    .then(result => {
        var task_status = result.status;

        temp_ambient = result.packet_info.temp;
        hum_ambient = result.packet_info.humidity;
        task_packet_fault = result.packet_info.fault;
        // var task_packet_checksum = result.packet_info.checksum;
        // var task_packet_eop = result.packet_info.eop;

        var task_good_packets = result.good_packets;
        task_bad_packets = result.bad_packets;

        var task_time_received = result.time_received;

        document.querySelector("#status").innerHTML = 
            `${task_status}`;

        document.querySelector("#packet-temp").innerHTML = 
            `${temp_ambient.toFixed(2)}`;
        document.querySelector("#packet-humidity").innerHTML = 
            `${hum_ambient.toFixed(2)}`;
        document.querySelector("#packet-fault").innerHTML = 
            `${task_packet_fault}`;
        // document.querySelector("#packet-checksum").innerHTML = 
        //     `${task_packet_checksum}`;
        // document.querySelector("#packet-eop").innerHTML = 
        //     `${task_packet_eop}`;

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

var fail_packet_alert_shown = false;
function update_failed_packet_notif()
{
    // Displays an alert if a packet has failed.
    if (task_bad_packets > 0) {
        if(!fail_packet_alert_shown) {
            $('#failed-packet').fadeIn();
            fail_packet_alert_shown = true;
        }
    } else {
        $('#failed-packet').hide();
        fail_packet_alert_shown = false;
    }
}

var fault_det_alert_shown = false;
function update_fault_det_notif()
{
    // Displays an alert if a fault is detected.
    if (task_packet_fault) {
        if(!fault_det_alert_shown) {
            $('#fault-detected').fadeIn();
            fault_det_alert_shown = true;
        }
    } else {
        $('#fault-detected').hide();
        fault_det_alert_shown = false;
    }
}