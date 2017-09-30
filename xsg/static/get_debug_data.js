function load_data() {
   $.getJSON($SCRIPT_ROOT + '/get_debug_data?game=' + $GAME, function (data){
      // console.log(data);
      $.each( data, function( key, val ) {
         if (key == 'week'){
           $("#"+key).text(val+1);
         }
         else {
           $("#"+key).text(val);
         }
      });
   })
};

$(function() {
  load_data();
  setInterval('load_data()', 5000); // run every 5 seconds
});
