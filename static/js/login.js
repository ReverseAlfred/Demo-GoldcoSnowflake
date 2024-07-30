$(document).ready(function() {
    // Check for flash message
    var flashMessage = $('#flash-message');
    
    if (flashMessage.length > 0) {
        // Ensure the flash message is visible
        flashMessage.addClass('show');
        
        // Fade in the flash message and then redirect if it's a success
        flashMessage.fadeIn().delay(3000).fadeOut(function() {
            if (flashMessage.hasClass('alert-success')) {
                // Delay the redirect to ensure the message is seen
                setTimeout(function() {
                    window.location.href = "/dashboard";
                }, 1000); // Adjust the delay if needed
            }
        });
    }
});
