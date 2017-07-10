console.log("Running Custom Script");

api_prefix="https://tdazhl5c8k.execute-api.us-east-1.amazonaws.com/dev"
star_keys = ['sketchiness', 'serviceQuality', 'responseTime', 'value', 'presentation', 'portionSize', 'primaryBaseRating', 'secondaryBaseRating', 'meatRating', 'sauceRating']

function loadvenues() {
    console.log("loading venues");
    endpoint = api_prefix+"/venues"
    $.get(endpoint, function(data) {
        $.each(data, function(i, venue) {
            $('#venueInput').append($('<option>', {
                value: venue.id,
                text: `${venue.name} (${venue.streetAddress}, ${venue.city} ${venue.state})`
            }));
        });
    });

}

function drawstars(value) {
    width = value * 16;
    return "<span class=\"stars\" style=\"width: 80px\" title=\""+value+"/5\"><span class=\"stars-inner\" style=\"width: "+width+"px\"></span></span>"
}

function loadpendingreview() {
    console.log("loading pending review");
    review_id = window.location.search.substring(4);
    console.log("loading review " + review_id)

    endpoint = api_prefix + "/fuckapproval/" + review_id;
    
    $.get(endpoint, function(data) {
        console.log(data);
        for (key in data) {
            $(`#${key}`).html(data[key]);
        }
        $.each(star_keys, function(i, key) {
            console.log(key);
            $(`#${key}`).html(drawstars(data[key]));
        });
        //$('#venue').html(data.venue);
        //#$('#date').html(data.date);
        //$('#reviewer').html(data.reviewer);
    });

    $('#accept').attr("href", api_prefix+"/accept/"+review_id);
    $('#reject').attr("href", api_prefix+"/reject/"+review_id);
}

$(function() {
    $("#venueSubmit").click(function(event) {
        console.log("Submitting venue");
        endpoint = api_prefix+"/venue";

        $.ajax({
            type: "POST",
            url: endpoint,
            data: $('#newVenueForm').serialize(),
            success: function(data, textStatus, xhr) {
                console.log("SUCCESS");
                console.log(data);
                $('#newVenueModal').modal('hide')
            },
            error: function(xhr, textStatus) {
                console.log("FAILURE");
                $('#newVenueError').html(xhr.responseText)
                $('#newVenueError').attr('hidden', null)
                console.log(xhr.status);
            }
        });
        
        event.preventDefault();
        console.log("End Submit venue");
    });

    $("#reviewSubmit").click(function(event) {
        console.log("Submitting review");
        endpoint = api_prefix + "/review"

        missingFields = ""

        $('#reviewForm').find('input').each(function() {
            if($(this).prop('required') != false) {
                missingFields += $(this).prop('name')
                missingFields += ", "
            }
        });
        
        if (missingFields != "") {
            $('#reviewError').html("You are missing required fields: " + missingFields);
            $('#errorModal').modal('show');
            return
        }

        $.ajax({
            type: "POST",
            url: endpoint,
            data: $('#reviewForm').serialize(),
            success: function(data, textStatus, xhr) {
                console.log("SUCCESS");
                document.location.href = "thanks.html";
            },
            error: function(xhr, textStatus) {
                console.log("FAILURE");
                console.log(xhr.status);
                console.log(xhr.responseText)

                $('#reviewError').html(xhr.responseText)
                $('#errorModal').modal('show');
            }
        });

        event.preventDefault();
        console.log("End Submit review");
    });
});

$(function()
	{
		// editable stars
		$('.stars.editable').each(function(i, e)
			{
				$(e).mousemove(function(e)
					{
						var offs = $(this).offset();
						var myval = 8 * (Math.round((e.pageX - offs.left) / 8));
						$('.stars-inner', this).css('width', myval);
						$(this).next('.stars-label').text(Math.round(myval / 8, 1) / 2);
					}).mouseout(function(e)
					{
						var offs = $(this).offset();

						if ( e.pageX >= offs.left && e.pageY >= offs.top && e.pageX <= offs.left + ($(this).attr('data-size') * 16) && e.pageY <= offs.top + 16 )
						{
							// don't do this function if we're still inside the element
							return;
						}

						$(this).next('.stars-label').text('');
						$('.stars-inner', this).css('width', Number($(this).next().next().val()) * 16);
					}).click(function(e)
						{
							var offs = $(this).offset();
							var myval = 8 * (Math.round((e.pageX - offs.left) / 8));
							$(this).next().next().val(Math.round(myval / 8, 1) / 2);
						}).mouseout();

			});
           });

console.log("Done running Custom Script");
