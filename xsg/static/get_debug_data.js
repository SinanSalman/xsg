function load_data() {
   $.getJSON($SCRIPT_ROOT + '/get_debug_data?game=' + $GAME, function (data){
      $.each( data, function( key, val ) {
         if (key == 'week'){
           $("#"+key).text(val+1);
         }
         else {
           $("#"+key).text(val);
         }
      });
   }).fail(function (d, textStatus, error) {
       console.error("getJSON failed, status: " + textStatus + ", error: " + error)
     });
};

$(function() {
  setInterval('load_data()', $REFRESH_INTERVAL); // run every $REFRESH_INTERVAL
});
