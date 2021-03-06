var xsgChart = null;

function PopupFunction(id) { document.getElementById(id).classList.toggle("show"); }

function sum( obj ) {
  var sum = 0;
  for( var el in obj ) {
    if( obj.hasOwnProperty( el ) ) {
      sum += parseFloat( obj[el] );
    }
  }
  return sum;
}

function SetFocus() {
  if ($('input[name="' + $SUPPLIERS[0] + '"]').length){ // does supplier have an input box?
      $('input[name="' + $SUPPLIERS[0] + '"]').select();
  }
  else if ($('input[name="' + $CUSTOMERS[0] + '"]').length){ // does customer have an input box?
      $('input[name="' + $CUSTOMERS[0] + '"]').select();
  }
}

function load_data() {
   $.getJSON($SCRIPT_ROOT + '/get_station_status?game=' + $GAME + '&station=' + $STATION, function (data){
      $.each( data, function( key, val ) {
          if (key == 'current_week'){
            $("#"+key).text(val+1);
          }
          else if (['incomming_order','incomming_delivery','backorder'].includes(key)){
            $.each( val, function( k, v ) {
              $(("#"+key+"_"+k).replace(/\./g,"\\.")).text(v);
            });
          } else if (key == 'ordering_limits'){
            $("#"+key).find(":not(:first)").remove();
            $("#"+key).append(val);
          } else if (key == 'shipping_limits'){
            $("#"+key).find(":not(:first)").remove();
            $("#"+key).append(val);
          } else if (key == 'connection_state') {
            $LAST_CONNECTION = val;
          } else if (key == 'turn_start_time') {
            $TURN_START_TIME = val;
          } else if (key == 'turn_time') {
            $TURN_TIME = val;
          } else if (key == 'server_time') {
            $ServerClientTimeDiff = (Date.now()/1000 - val);
          } else{
             $("#"+key).text(val);
          };
      });
      $WEEK = data.current_week
      $INVENTORY = data.inventory
      $ORDERS = data.incomming_order
      $BACKORDERS = data.backorder
      $ORDER_MIN = data.order_min
      $ORDER_MAX = data.order_max
      $SHIP_MIN = data.ship_min
      $SHIP_MAX = data.ship_max

      xsgChart.data.datasets.forEach((dataset) => {
        if (dataset.label == "Inventory"){ dataset.data = [$INVENTORY]; }
        else { dataset.data = [-sum($BACKORDERS)]; } });
      xsgChart.update();

      var button = document.getElementById('submit');
      if ( data.game_done ){
         button.style.backgroundColor = "#822D1A";
         button.textContent = "DONE";
         button.disabled = true;
      }
      else if ( $WEEK == $WEEKCOUNTER ){
         button.style.backgroundColor = "#9BE6BB";
         button.textContent = "Send";
         button.disabled = false;
         if ($TURN_START_TIME > 0 && $TURN_TIME > 0){
           var TIME_LEFT = Math.round($TURN_TIME - (Date.now() / 1000 - $TURN_START_TIME) + $ServerClientTimeDiff);
           $("#time_left").text(TIME_LEFT);
           if (TIME_LEFT < 0){
             var data = { week: $WEEK };
             data['customers'] = {}
             for (i = 0; i < $CUSTOMERS.length; i++) {data['customers'][$CUSTOMERS[i]] = 0;};
             data['suppliers'] = {}
             for (i = 0; i < $SUPPLIERS.length; i++) {data['suppliers'][$SUPPLIERS[i]] = 0;};
             $.ajax({
               url: $SCRIPT_ROOT + '/submit',
               type: 'POST',
               contentType: "application/json; charset=utf-8",
               dataType: "json",
               data: JSON.stringify({ DATA: data }),
               success: function (data) {
                 $WEEKCOUNTER++;
                 var button = document.getElementById('submit');
                 button.style.backgroundColor = "#822D1A";
                 button.disabled = true;
                 // setTimeout(function () { button.focus(); }, 1000);
               }
             });
           }
         }
         else {
           $("#time_left").text('-');
         }
      }
      else if ( ($WEEK > $WEEKCOUNTER) || ($WEEK < $WEEKCOUNTER - 1) ){
         if ( !$OUT_OF_SYNC_MSG ){
            button.style.backgroundColor = "#822D1A";
            button.textContent = "Out of Sync";
            button.disabled = true;
            $OUT_OF_SYNC_MSG = true;
            alert('Your screen is out of sync with the server, you\'re screen will be reloaded to fix the issue.');
            window.location.href = $SCRIPT_ROOT + '/play_screen'
            return;
         }
         else {return;}
      };
   })
    .fail(function (d, textStatus, error) {
       console.error("getJSON failed, status: " + textStatus + ", error: " + error)
    })
    .always(function() {
      if (Date.now()/1000 - $LAST_CONNECTION < $AWAY_LIMIT){
         $("#connection_state").text('connected');
      }
      else{
         $("#connection_state").text('DISCONNECTED');
      }
    });
};

function send_data() {
   var data = { week:$WEEK };
   var total_shipments = 0;
   var total_orders = 0;
   var total_customers_orders_backorders = 0;
   data['customers'] = {}
   for (i = 0; i < $CUSTOMERS.length; i++){
      if ($('input[name="' + $CUSTOMERS[i] + '"]').length){ // does customer have an input box?
        var value = Number($('input[name="' + $CUSTOMERS[i] + '"]').val());
        if ( value < 0 ){
           alert('Cannot ship negative ammount!'); return;
        };
        if (value > $ORDERS[$CUSTOMERS[i]] + $BACKORDERS[$CUSTOMERS[i]]){
           alert('Shipment to \'' + $CUSTOMERS[i] + '\' is more than their total request (PO+BackOrder)!'); return;
        };
        data['customers'][$CUSTOMERS[i]] = value;
        total_shipments += value;
        total_customers_orders_backorders += $ORDERS[$CUSTOMERS[i]] + $BACKORDERS[$CUSTOMERS[i]]
      };
   };
   data['suppliers'] = {}
   for (i = 0; i < $SUPPLIERS.length; i++){
     if ($('input[name="' + $SUPPLIERS[i] + '"]').length){ // does supplier have an input box?
        var value = Number($('input[name="' + $SUPPLIERS[i] + '"]').val());
        if ( value < 0 ){
           alert('Cannot order negative ammount!'); return;
        };
        data['suppliers'][$SUPPLIERS[i]] = value;
        total_orders += value;
      };
   };
   if ($('input[name="' + $CUSTOMERS[0] + '"]').length){ // does player decide shipments to customers?
     if ( total_shipments > $INVENTORY ){
        alert('Cannot ship more than what you have in inventory!'); return;
     };
     if ( ( $SHIP_MIN > $INVENTORY ) && ( total_shipments != 0 ) ) {
        alert('Your inventory is below the shipping mimumum limit, therefore you cannot ship. Please enter 0 units for this week shipments!'); return;
     }
     if ( ( $SHIP_MIN > total_customers_orders_backorders ) && ( total_shipments != 0 ) ) {
        alert('Your total customers demand (POs+BackOrders) is below the shipping mimumum limit, therefore you cannot ship. Please enter 0 units for this week shipments!'); return;
     }
     if ( (total_shipments < $SHIP_MIN) || (total_shipments > $SHIP_MAX) ){
        if ( total_shipments != 0 ){ // zero shipments is considered a 'turn pass' and allowed when out of limits; for the case when $SHIP_MIN > $INVENTORY
            alert('Your shipments total is out of shipping limits!'); return;
        }
     };
   }
   if ($('input[name="' + $SUPPLIERS[0] + '"]').length){ // does player decide orders to suppliers?
     if ( (total_orders < $ORDER_MIN) || (total_orders > $ORDER_MAX) ){
        alert('Your order total is out of ordering limits!'); return;
     };
   }
   $.ajax({
          url: $SCRIPT_ROOT + '/submit',
          type: 'POST',
          contentType: "application/json; charset=utf-8",
          dataType: "json",
          data: JSON.stringify({DATA:data}),
          success: function(data) {
             $WEEKCOUNTER++;
             var button = document.getElementById('submit');
             button.style.backgroundColor = "#822D1A";
             button.disabled = true;
             // setTimeout(function() { button.focus(); },1000);
          }
   });
   SetFocus();
};

$(function() {
   var ctx = document.getElementById("xsgChart").getContext('2d');
	  chrtcfg = {type: 'horizontalBar',
               data: { labels: [''],
                     datasets: [{label:"Inventory",data:[0],borderColor:"#BFA500",backgroundColor:"#BFA500"},
                               {label:"Backorder",data:[0],borderColor:"#BF4D00",backgroundColor:"#BF4D00"}] },
            options: { legend: {position: 'bottom', labels: {boxWidth: 10} },
                       scales: { yAxes: [{ stacked: true, categoryPercentage: 1.0, barPercentage: 1.0}],
                                 xAxes: [{ticks: {suggestedMin: -200, suggestedMax: 200 } }]},
                     maintainAspectRatio: false }};
	 xsgChart = new Chart(ctx,chrtcfg);

   $('button#submit').on("click", send_data)
   setInterval('load_data()', $REFRESH_INTERVAL); // run this every $REFRESH_INTERVAL
   SetFocus();
});
