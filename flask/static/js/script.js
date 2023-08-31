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

function populateUserServices(json, board, status) {
    board.empty();
    $.each(json, function(index, item) {
        var activate_pause = "";
        if (status == "active") {
            activate_pause = `<a class='user-service-change' href="/user/service/pause/${item.id}"><i class="fa-regular fa-circle-pause"></i></a>`
        } else {
            activate_pause = `<a class='user-service-change' href="/user/service/activate/${item.id}"><i class="fa-regular fa-circle-play"></i></a>`
        }

        const elem = $('<tr>');
        elem.html(`
            <td>${item.title}</td>
            <td>${item.description}</td>
            <td>
                <a class='user-service-change' href="/user/service/update/${item.id}"><i class="fa-regular fa-pen-to-square"></i></a>
                ${activate_pause}
                <a class='user-service-change' href="/user/service/delete/${item.id}"><i class="fa-regular fa-trash-can"></i></a>
            </td>
        `);
        board.append(elem);
    });
}

function ajaxUserServices(path, board, replace_state) {
    var api_path = "/api".concat(path)
    var status = path.substring(path.lastIndexOf('/') + 1);
    $.ajax({
        url: api_path,
        method: 'GET',
        dataType: 'json',
        success: function(response) {
            populateUserServices(response, board, status);
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

function updateUserServiceNav(path) {
    $('#user-service-nav .user-service-status').each(function() {
        if ($(this).attr('href') == path)
            $(this).addClass('active-subnav-header');
        else
            $(this).removeClass('active-subnav-header')
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

    var path = document.location.pathname;
    if (path.startsWith('/service/list/')) {
        var serviceBoard = $('#services-board')
        var path = document.location.pathname;
        ajaxServicesBoard(path, serviceBoard, true);
        $('#service-category-dropdown').val(path);
        $('#service-category-dropdown').change(function() {
            ajaxServicesBoard($(this).val(), serviceBoard);
        });
    } else if (path.startsWith('/user/service/list/')) {
        var userServiceNav = $("#user-service-nav")
        var userServiceTable = $('#user-service-table tbody')
        ajaxUserServices(path, userServiceTable, true);
        updateUserServiceNav(path);
        $('#user-service-nav .user-service-status').on('click', function(event) {
            event.preventDefault();
            var path = $(this).attr('href')
            ajaxUserServices(path, userServiceTable)
            updateUserServiceNav(path);
        });
    }


    window.onpopstate = (event) => {
        var path = document.location.pathname;
        if (path.startsWith('/service/list/')) {
            $('#service-category-dropdown').val(path);
            populateServicesBoard(event.state, serviceBoard);
        } else if (path.startsWith('/user/service/list/')) {
            var status = path.substring(path.lastIndexOf('/') + 1);
            updateUserServiceNav(path)
            populateUserServices(event.state, userServiceTable, status);
        }
    };
})
