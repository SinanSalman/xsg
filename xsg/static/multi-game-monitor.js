function reset_game(game) {
	if (confirm("All player(s) data in " + game + " will be lost, press [OK] to continue or [Cancle] to abort.")) {
		$.post($SCRIPT_ROOT + '/reset_game?game_name=' + game, function (data) {
			$("#reset_msg").text(data.Result);
			setTimeout(function () {$("#reset_msg").text('')}, 10000);
		})
	}
}

function load_data() {
	$.getJSON($SCRIPT_ROOT + '/get_games_status?games_list=' + $GAMES_LIST, function (data) {
		$.each(data, function (game, gamedata) {
			$.each(gamedata, function (key, val) {
				if (['week', 'waiting', 'disconnected'].includes(key)) {
					$("#" + key + "_" + game).text(val);
				}
				if (['inventory', 'backorder', 'trucks', 'cost'].includes(key)) {
					$("#" + key + "_" + game).text(Math.round(val).toLocaleString());
				}
				if (['fulfillment', 'greenscore'].includes(key)) {
					$("#" + key + "_" + game).text(Math.round(val * 100));
				}
			})
		})
	}).fail(function (d, textStatus, error) {
		console.error("getJSON failed, status: " + textStatus + ", error: " + error)
	})
};

$(function () {
	setInterval('load_data()', 5000); // run this every 5 seconds
});