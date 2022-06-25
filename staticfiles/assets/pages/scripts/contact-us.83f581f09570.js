var ContactUs = function () {

    return {
        //main function to initiate the module
        init: function () {
			var map;
			$(document).ready(function(){
			  map = new GMaps({
				div: '#map',
	            lat: 37.552673,
				lng: 45.076046,
			  });
			   var marker = map.addMarker({
		            lat: 37.552673,
					lng: 45.076046,
		            title: 'Loop, Inc.',
		            infoWindow: {
		                content: "<b>Urmia</b>"
		            }
		        });

			   marker.infoWindow.open(map, marker);
			});
        }
    };

}();