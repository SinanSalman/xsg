var $DATA = {};
var $WEEK = 0;
var xsgChart0 = null;
var xsgChart1 = null;
var xsgChart2 = null;
var previous_plot = null;
var PALETTE_NAME = 'tol-rainbow';

function avg(A) {
	var sum = 0.0;
	var n = 0.0;
	keys = Object.keys(A);
	for (var k in keys){
			sum += A[keys[k]];
			n++;
	}
	return sum/n
}

function sum(A) {
	var sum = 0.0;
	keys = Object.keys(A);
	for (var k in keys){
			sum += A[keys[k]];
	}
	return sum;
}

function sum_elem(A) {
	var sum = [];
	var keys = Object.keys(A);
	for (i=0;i<A[keys[0]].length;i++){
		sum.push(0);
		for (var k in keys){
			sum[i] += A[keys[k]][i];
		}
	}
	return sum
}

function avg_elem(A) {
	var avg = [];
	var keys = Object.keys(A);
	var keys_count = keys.length;
	for (i=0;i<A[keys[0]].length;i++){
		avg.push(0);
		for (var k in keys){
			avg[i] += A[keys[k]][i];
		}
		avg[i] /= keys_count;
	}
	return avg
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

function hidallstationsdata(){
		$.each(xsgChart2.data.datasets, function(k,v){
		a = v._meta[2];
		a.hidden = null === a.hidden ? !v.hidden : null;
		xsgChart2.update();
	})
}

function load_data() {
	$.getJSON($SCRIPT_ROOT + '/get_game_status?game=' + $GAME, function (data){
		$("#Week").text(data.week+1);
		$("#WaitingFor").text(data.waitingfor);
		$("#Disconnected").text(data.disconnected);

		$.each( data.data, function( key, val ) {
			if (['cost_inventory_sum','cost_backorder_sum','cost_transport_sum','cost_total_sum'].includes(key)){
				$.each( val, function( k, v ) {
					$(("#"+key+"_"+k).replace(/\./g,'\\.')).text(Math.round(v).toLocaleString());
				})
			}
			if (['fulfilment_avg','green_score_avg'].includes(key)){
				$.each( val, function( k, v ) {
					$(("#station_"+k).replace(/\./g,'\\.')).text(k+' ('+$PLAYERS[k]+')'); // repeats for each row resetting to the same value, but it is okay
					$(("#"+key+"_"+k).replace(/\./g,'\\.')).text(Math.round(v*100));
				})
			}
		})

		$WEEK = data.week;
		if ($WEEK > 0) {
			$("#tot_cost_inventory").text(Math.round(sum(data.data.cost_inventory_sum)).toLocaleString());
			$("#tot_cost_backorder").text(Math.round(sum(data.data.cost_backorder_sum)).toLocaleString());
			$("#tot_cost_transport").text(Math.round(sum(data.data.cost_transport_sum)).toLocaleString());
			$("#tot_cost_total").text(Math.round(sum(data.data.cost_total_sum)).toLocaleString());
			$("#avg_fulfilment").text(Math.round(avg(data.data.fulfilment_avg)*100));
			$("#avg_green_score").text(Math.round(avg(data.data.green_score_avg)*100));

			$DATA = data.data;
			update_plot();
		} else {
			$("[id^=tot_cost_]").each(function() { $(this).text('n/a'); });
			$("[id^=avg_]").each(function() { $(this).text('n/a'); });
			$("[id^=cost_]").each(function() { $(this).text('n/a'); });
			$("[id^=green_score_]").each(function() { $(this).text('n/a'); });
			$("[id^=fulfilment_]").each(function() { $(this).text('n/a'); });

			xsgChart0.data.datasets[0].data = [];
			for (x in xsgChart1.data.datasets){
				xsgChart1.data.datasets[x].data = []; }
			for (x in xsgChart2.data.datasets){
				xsgChart2.data.datasets[x].data = []; }
			xsgChart0.update();
			xsgChart1.update();
			xsgChart2.update();
		}
	}).fail(function (d, textStatus, error) {
			console.error("getJSON failed, status: " + textStatus + ", error: " + error)
		})
};

function update_plot() {
	var e = document.getElementById("data_item");
	var data_item = e.options[e.selectedIndex].text;
	if (!$DATA.hasOwnProperty('orders')) return;  // data not initialized yet
	if (($WEEK == xsgChart1.data.labels.length) && (xsgChart0.data.datasets[0].data.length > 0) && (previous_plot == data_item)) return;  // data didn't change

	xsgChart0.data.labels=Object.keys($DATA.cost_total_sum).map(function(x) {return x +'('+$PLAYERS[x]+')';});
	xsgChart0.data.datasets[0].data=Object.values($DATA.cost_total_sum);
	seq = palette(PALETTE_NAME, xsgChart0.data.labels.length).map(function(hex) { return '#' + hex; });
	xsgChart0.data.datasets[0].borderColor = seq;
	xsgChart0.data.datasets[0].backgroundColor = seq;

	if (previous_plot != data_item){
		xsgChart1.data.datasets = [];
		xsgChart2.data.datasets = [];
	}
	xsgChart1.data.labels = Array.from(Array($WEEK).keys()).map(function(x) { return String(x+1) });
	xsgChart2.data.labels = Array.from(Array($WEEK).keys()).map(function(x) { return String(x+1) });

	var chart1data = {}
	var chart2data = {}

	if (data_item == 'orders'){
		$DEMANDS.forEach(function(val){
			chart2data[val+'('+$PLAYERS[val]+')'] = $DATA[data_item][val].slice(0,$WEEK);});
	}

	if (data_item == 'inventory/backorders'){
		chart1data['inventory'] = sum_elem($DATA.inventory).slice(0,$WEEK);
		chart1data['backorders'] = sum_elem($DATA.backorder).slice(0,$WEEK).map(function(x) {return x * -1;});
		$STATIONS.forEach(function(val){
			chart2data[val+'('+$PLAYERS[val]+'):I'] = $DATA.inventory[val].slice(0,$WEEK);
			chart2data[val+'('+$PLAYERS[val]+'):B'] = $DATA.backorder[val].slice(0,$WEEK).map(function(x) {return x * -1;});});
  	}
	else if (data_item == 'inventory-backorders'){
			var I_B = {};
			$STATIONS.forEach(function(val){
				for (i=0; i<= $WEEK; i++){
					if (i==0) {I_B[val] = []}
					I_B[val].push($DATA.inventory[val][i]-$DATA.backorder[val][i]) } });
			chart1data['inventory-backorders'] = sum_elem(I_B).slice(0,$WEEK);
			$STATIONS.forEach(function(val){
				chart2data[val+'('+$PLAYERS[val]+')'] =I_B[val].slice(0,$WEEK); });
  	}
	else {
		if (['fulfilment','green_score'].includes(data_item)){
			chart1data[data_item] = avg_elem($DATA[data_item]).slice(0,$WEEK);
		} else {
			chart1data[data_item] = sum_elem($DATA[data_item]).slice(0,$WEEK);
		}
		$STATIONS.forEach(function(val){
			chart2data[val+'('+$PLAYERS[val]+')'] = $DATA[data_item][val].slice(0,$WEEK);});
  	}

	var unit = ' (units)';
	if (['shipments','extra-shipments'].includes(data_item)) { unit = ' (trucks)'; }
	if (['fulfilment','green_score'].includes(data_item)) { unit = ' (%)'; }
	if (['cost'].includes(data_item)) { unit = ' ($)'; }

	if (previous_plot == data_item){
		var index = 0;
		for (var key in chart1data){
			index = find_object_index(xsgChart1.data.datasets,'label',key);
			xsgChart1.data.datasets[index].data = chart1data[key]; }
		for (var key in chart2data){
			index = find_object_index(xsgChart2.data.datasets,'label',key);
 			xsgChart2.data.datasets[index].data = chart2data[key]; }
	} else {
		for (var key in chart1data){
			xsgChart1.data.datasets.push({label:key,data:chart1data[key]}) }
		for (var key in chart2data){
			xsgChart2.data.datasets.push({label:key,data:chart2data[key]}) }
	}

	if (previous_plot != data_item){
		xsgChart1.options.title.text = 'XSG - ' + data_item + unit;
		var count = xsgChart1.data.datasets.length;
	  	seq = palette(PALETTE_NAME, count).map(function(hex) { return '#' + hex; });
	  	for (i=0; i<count; i++){
		 	xsgChart1.data.datasets[i].borderColor = seq[i];
		 	xsgChart1.data.datasets[i].backgroundColor = hex2rgba(seq[i],0.5);
	  	}
		if (data_item == 'inventory/backorders'){
			var count = xsgChart2.data.datasets.length/2;
		  	seq = palette(PALETTE_NAME, count*2).map(function(hex) { return '#' + hex; });
		  	for (i=0; i<(count*2); i+=2){
				xsgChart2.data.datasets[i].borderColor = seq[i];
			 	xsgChart2.data.datasets[i].backgroundColor = seq[i];
				xsgChart2.data.datasets[i+1].borderColor = seq[i];
			 	xsgChart2.data.datasets[i+1].backgroundColor = seq[i];
			}
		} else {
			var count = xsgChart2.data.datasets.length;
		  	seq = palette(PALETTE_NAME, count).map(function(hex) { return '#' + hex; });
		  	for (i=0; i<count; i++){
			 	xsgChart2.data.datasets[i].borderColor = seq[i];
			 	xsgChart2.data.datasets[i].backgroundColor = seq[i];
		  	}
		}
	}

	xsgChart0.update();
	xsgChart1.update();
	xsgChart2.update();
	previous_plot = data_item;
}

$(function() {
	var ctx0 = document.getElementById("xsgChart0").getContext('2d');
	var ctx1 = document.getElementById("xsgChart1").getContext('2d');
	var ctx2 = document.getElementById("xsgChart2").getContext('2d');
	chrt0cfg = {type: 'doughnut',
					data: { labels: [], datasets: [{ data:[] }] },
							 options: {  title: { display: true },
							  legend: {position: 'right', labels: { boxWidth: 20 }, display: false },
								tooltips: {
								  callbacks: {
								    label: function(tooltipItem, data) {
								      //get the concerned dataset
								      var dataset = data.datasets[tooltipItem.datasetIndex];
								      //calculate the total of this data set
								      var total = dataset.data.reduce(function(previousValue, currentValue, currentIndex, array) {
								        return previousValue + currentValue;
								      });
								      //get the current items value
								      var currentValue = dataset.data[tooltipItem.index];
								      //calculate the precentage based on the total and current item, also this does a rough rounding to give a whole number
								      var precentage = Math.floor(((currentValue/total) * 100)+0.5);

								      return data.labels[tooltipItem.index] + ': ' + precentage + "%";
								    }
								  }
								}
							}}
	chrt1cfg = {type: 'line',
					data: { labels: [], datasets: []},
							 options: {  title: { display: true },
										 elements: {    line: { tension: 0.1, fill: true},
											  				point: {  radius: 0} },
										   legend: {position: 'bottom', labels: {boxWidth: 20} },
										   scales: {   yAxes: [{ ticks: { beginAtZero: true }}]} } };
	chrt2cfg = {type: 'line',
					data: { labels: [], datasets: [] },
							 options: {  title: { display: false },
										 elements: {    line: { tension: 0.1, fill: false},
														   point: {  radius: 0} },
										   legend: {position: 'bottom', labels: {boxWidth: 20} },
										   scales: { yAxes: [{ ticks: { beginAtZero: true }}]} } };
	if ($WEEKS > 20){
		chrt1cfg.options.scales['xAxes'] = [{ ticks: { callback: function(tick, index, array) { return (index % 2) ? "" : tick;} } }]
		chrt2cfg.options.scales['xAxes'] = [{ ticks: { callback: function(tick, index, array) { return (index % 2) ? "" : tick;} } }]
	}

	xsgChart0 = new Chart(ctx0,chrt0cfg);
	xsgChart1 = new Chart(ctx1,chrt1cfg);
	xsgChart2 = new Chart(ctx2,chrt2cfg);

	setInterval('load_data()', $REFRESH_INTERVAL); // run this every $REFRESH_INTERVAL
});
