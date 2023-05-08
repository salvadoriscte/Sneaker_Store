$(document).ready(function () {
    const djangoMessages = $("#django-messages > div").map(function () {
        return {
            content: $(this).data("content"),
            type: $(this).data("type")
        };
    }).get();

    if (djangoMessages.length > 0) {
        djangoMessages.forEach(function (message) {
            displayPopup(message.content, message.type);
        });
    }

    function displayPopup(content, type) {
        const popup = $('<div>', {
            class: `popup ${type}`,
            text: content
        });

        $('body').append(popup);
        popup.fadeIn();

        setTimeout(function () {
            popup.fadeOut(function () {
                popup.remove();
            });
        }, 4000);
    }
});