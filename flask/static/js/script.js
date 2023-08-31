function populateServicesBoard(json, board) {
    board.empty();
    $.each(json, function(index, item) {
        const elem = $('<div class="post">');
        elem.html(`
            <img src="/static/img/terminal.jpg" alt="Post 1">
            <h3>${item.title}</h3>
            <p>${item.description}</p>
            <p>Offered by: ${item.username}</p>
        `);
        board.append(elem);
    });
}

function ajaxServicesBoard(path, board, replace_state) {
    var api_path = "/api".concat(path)
    $.ajax({
        url: api_path,
        method: 'GET',
        dataType: 'json',
        success: function(response) {
            populateServicesBoard(response, board);
            if (replace_state)
                history.replaceState(response, null, path);
            else
                history.pushState(response, null, path);
        },
        error: function(xhr, status, error) {
            console.error('Error fetching data:', error);
        }
    });
}

$(document).ready(function() {
    $('#modal-popout-trigger').on('click', function(event) {
        event.preventDefault();
        var popout = $('#modal-popout');
        if (popout.css('display') == 'none')
            popout.css('display', 'block');
        else
            popout.css('display', 'none');
    });

    var board = $('#services-board')
    if (board.length > 0) {
        var path = document.location.pathname;
        ajaxServicesBoard(path, board, true);
        $('#service-category-dropdown').val(path);
        $('#service-category-dropdown').change(function() {
            ajaxServicesBoard($(this).val(), board);
        });
    }

    window.onpopstate = (event) => {
        var path = document.location.pathname;
        if (path.startsWith('/service/list/')) {
            $('#service-category-dropdown').val(path);
            populateServicesBoard(event.state, board);
        }
    };
})
