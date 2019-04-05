var hours = 24;
var granularity = '5m';
var end = 0;
var graphdata = "https://bastart.spoton.cz/data/solar_monitor?range=24h&granularity=5m&end=0h";
sol = new Dygraph(
// containing div
document.getElementById("solar"),
// CSV or path to a CSV file.
graphdata
,{
    //labels: ['time','V_solar','Isolar', P_solar, P_cons],
    axes : {
        x : {
            drawGrid: true,
            drawAxis : true
        },
        y : {
            drawGrid: false,
            drawAxis : true,
            valueRange: [46,55]
        },
        y2 : {
            drawGrid: false,
            drawAxis: true,
            independentTicks: true,
            valueRange: [0,1300]
        }
    },
    rollPeriod: 3,
    visibility: [false, false, true, true],
    interactionModel: {},
    connectSeparatedPoints: true,
    series:{
        'V_solar': {
            axis: 'y',
            color: '#ffd020',
            fillGraph: true,
            fillAlpha: 0.4
        },
        'I_solar': {
            axis: 'y',
            color: '#ff1100'
        },
        'P_solar': {
            axis: 'y2',
            color: '#1111ff',
            fillGraph: true,
            fillAlpha: 0.4
        },
        'V_array': {
            axis: 'y',
            color: '#ff1111',
            fillGraph: true,
            fillAlpha: 0.4
        }

    },
        ylabel: '<span style="color:#ffd020;">Solar [V]</span>/<span style="color:#ff1100;">Batt [V]</span>',
        y2label: '<span style="color:#111177;">Solar / Consumption [W]</span>',
        labelsDiv: 'solar_labels',
        legend: 'always'
    }
);


function refreshGraph(){
  graphdata = "https://bastart.spoton.cz/data/solar_monitor?range=" + hours + "h&granularity=" + granularity + "&end=" + end + "h";
  sol.updateOptions({'file': graphdata});
  //power.updateOptions({'file': graphdata});
}

function setHours(hours_to_set){
  hours = hours_to_set;
  switch(hours){
      case '1':
        granularity = '10s';
        break;
      case '6':
        granularity = '10s';
        break;
      case '12':
        granularity = '2m';
        break;
      case '24':
        granularity = '5m';
        break;
      case '168':
        granularity = '15m';
        break;
      case '720':
        granularity = '30m';
        break;
      default:
        granularity = '5m';
  }
  end = 0;
  //document.getElementById('xxx').innerHTML = graphdata;
  refreshGraph();
}

function setBack(){
    // range=1h -> range=2h&end=1h
    disp_range = hours*1 - end*1;
    hours = hours*1 + disp_range;
    end = end*1 + disp_range;
    //document.getElementById('xxx').innerHTML = graphdata;
    refreshGraph();
}

function setForth(){
    disp_range = hours*1 - end*1;
    hours = hours*1 - disp_range;
    if(hours < disp_range){
        hours = disp_range;
    }
    end = end*1 - disp_range;
    if(end < 0){
        end = 0;
    }
    //document.getElementById('xxx').innerHTML = graphdata;
    refreshGraph();
}

function getPageContents(callback,url,params) {
    if (window.XMLHttpRequest){
        // code for IE7+, Firefox, Chrome, Opera, Safari, SeaMonkey
        xmlhttp=new XMLHttpRequest();
    }
    else{
        // code for IE6, IE5
        xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
    }
    if(params!=null) {
        xmlhttp.open("POST", url, true);
        xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    } else {
        xmlhttp.open("GET", url, true);
    }
    xmlhttp.onreadystatechange = function() {
        if(xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            callback(xmlhttp.responseText);
        }
    }
    xmlhttp.send(params);
}

counter = 0;
function refreshValues(){
    fresh_vals_url = '/data/solar_realtime_data?type=json'
    getPageContents(function(result){freshVals=JSON.parse(result);},
                     fresh_vals_url)
    document.getElementById('timestamp').innerHTML = freshVals.time;                 
    document.getElementById('array_voltage').innerHTML = freshVals.V_array;
    document.getElementById('array_percent').innerHTML = freshVals.perc_array;
    document.getElementById('charge_current').innerHTML = freshVals.ChCurr;
    document.getElementById('solar_power').innerHTML = freshVals.Psol;
    document.getElementById('pmax_day').innerHTML = freshVals.Pmax_day;
    counter = counter + 30000;
    if(counter >= 360000){
        refreshGraph();
        document.getElementById('graph_timestamp').innerHTML = freshVals.time;        
        counter = 0;
    }
}



var intervalVal = setInterval(refreshValues, 30000);
