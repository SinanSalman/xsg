var $WEEKS = 0
var $DATA = {};
var xsgChart = null;
var previous_plot = null;
var PALETTE_NAME = 'tol-rainbow';
var graph_list = {'cost':'totalcost','fulfilment':'avgfulfilment','green_score':'avggreenscore'};
var title = {'cost':'Total Supply Chain Cost','green_score':'Avg Green Score','fulfilment':'Avg Fulfilment'}

function reset_game(game) {
	if (confirm("All player(s) data in " + game + " will be lost, press [OK] to continue or [Cancle] to abort.")) {
		$.post($SCRIPT_ROOT + '/reset_game?game_name=' + game, function (data) {
			$("#reset_msg").text(data.Result);
			setTimeout(function () {$("#reset_msg").text('')}, 10000);
		})
	}
}

function hex2rgba(hex, alpha) {
    var r = parseInt(hex.slice(1, 3), 16),
        g = parseInt(hex.slice(3, 5), 16),
        b = parseInt(hex.slice(5, 7), 16);
    if (alpha) {
        return "rgba(" + r + ", " + g + ", " + b + ", " + alpha + ")";
    } else {
        return "rgb(" + r + ", " + g + ", " + b + ")";
    }
}

function find_object_index(array_of_objects,key,val){
    for (var i=0; i<array_of_objects.length; i++) {
        if(array_of_objects[i][key] == val){
            return i;
            break;
        }
    }
}

function update_plot() {
	var e = document.getElementById("data_item");
	var data_item = e.options[e.selectedIndex].text;

	if (previous_plot != data_item){
		xsgChart.data.datasets = [];
	}

	var chartdata = {};
	for (i in $GAMES_LIST){
		chartdata[$GAMES_LIST[i]] = $DATA[$GAMES_LIST[i]][graph_list[data_item]];
		len = chartdata[$GAMES_LIST[i]].length;
		if (len > $WEEKS) {$WEEKS = len;}
  }
	xsgChart.data.labels = Array.from(Array($WEEKS).keys()).map(function(x) { return String(x+1) });

	if (previous_plot == data_item){
		for (var key in chartdata){
			index = find_object_index(xsgChart.data.datasets,'label',key);
			xsgChart.data.datasets[index].data = chartdata[key]; }
	} else {
		for (var key in chartdata){
			xsgChart.data.datasets.push({label:key,data:chartdata[key]}) }
	}

	if (previous_plot != data_item){
		xsgChart.options.title.text = 'XSG - ' + title[data_item];
		var count = xsgChart.data.datasets.length;
	  	seq = palette(PALETTE_NAME, count).map(function(hex) { return '#' + hex; });
	  	for (i=0; i<count; i++){
		 	xsgChart.data.datasets[i].borderColor = seq[i];
		 	xsgChart.data.datasets[i].backgroundColor = hex2rgba(seq[i],0.5);
	  	}
	}

	xsgChart.update();
	previous_plot = data_item;
}

function load_data() {
	$.getJSON($SCRIPT_ROOT + '/get_games_status?games_list=' + $GAMES_LIST, function (data) {
		$.each(data, function (game, gamedata) {
			$.each(gamedata, function (key, val) {
				if (['week'].includes(key)) {
					$("#" + key + "_" + game).text(val);
				}
				if (['waiting', 'disconnected'].includes(key)) {
					$("#"+key+ "_" + game).find(":not(:first)").remove();
					$("#"+key+ "_" + game).append(val);
				}
				if (['inventory', 'backorder', 'trucks', 'cost'].includes(key)) {
					$("#" + key + "_" + game).text(Math.round(val).toLocaleString());
				}
				if (['fulfilment', 'greenscore'].includes(key)) {
					$("#" + key + "_" + game).text(Math.round(val * 100));
				}
			})
		})
		$DATA = data;
		update_plot();
	}).fail(function (d, textStatus, error) {
		console.error("getJSON failed, status: " + textStatus + ", error: " + error)
	})
};

$(function () {
	var ctx = document.getElementById("xsgChart").getContext('2d');
	chrtcfg = {type: 'line',
					data: { labels: [], datasets: [] },
							 options: {  title: { display: true },
										 elements: {    line: { tension: 0.1, fill: false},
															 point: {  radius: 0} },
											 legend: {position: 'bottom', labels: {boxWidth: 20} },
											 scales: { yAxes: [{ ticks: { beginAtZero: false }}]} } };
	xsgChart = new Chart(ctx,chrtcfg);

	setInterval('load_data()', $REFRESH_INTERVAL); // run this every $REFRESH_INTERVAL
});
