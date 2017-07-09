console.log("Running Custom Script");

api_prefix="https://tdazhl5c8k.execute-api.us-east-1.amazonaws.com/dev"

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

console.log("Done running Custom Script");
