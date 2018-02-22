var xsgChart = null
var PALETTE_NAME = 'tol-rainbow';

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

function load_data() {
	$.getJSON($SCRIPT_ROOT + '/get_game_status_radar?game=' + $GAME, function (data){
		if (!data.hasOwnProperty('nodata')){
			var D = xsgChart.data;
			if (D.labels.length == 0){
				$.each( data, function( key, val ) {
					D.labels=Object.keys(val);
					D.datasets.push({label:key+'('+$PLAYERS[key]+')',data:Object.values(val)});
				});
			}
			else {
				$.each( data, function( key, val ) {
					var index = find_object_index(D.datasets,'label',key+'('+$PLAYERS[key]+')');
					D.datasets[index].data = Object.values(val);
				});
			}
			seq = palette(PALETTE_NAME, D.datasets.length).map(function(hex) { return '#' + hex; });
			for (i=0; i<D.datasets.length; i+=1){
				D.datasets[i].borderColor = seq[i];
				D.datasets[i].backgroundColor = hex2rgba(seq[i],0.3);
			}
			xsgChart.update();
		}
	 }).fail(function (d, textStatus, error) {
			console.error("getJSON failed, status: " + textStatus + ", error: " + error)
		});
};

$(function() {
	chrtcfg = {type: 'radar',
					   data: { labels: [], datasets: [] },
							      options: {  title: { display: true },
								     legend: {position: 'right', labels: { boxWidth: 20 } } } }
	xsgChart = new Chart(document.getElementById("xsgChart").getContext('2d'),chrtcfg)
	setInterval('load_data()', 5000); // run this every 5 seconds
});
