const popout = document.getElementById('modal-popout');
const trigger = document.getElementById('modal-popout-trigger');

if (trigger != null) {
    trigger.addEventListener('click', function(event) {
        event.preventDefault();
        if (popout.style.display == 'none')
            popout.style.display = 'block';
        else
            popout.style.display = 'none'
    });
}

$(document).ready(function() {
    $('#service-category-dropdown').change(function(){
        $.ajax({
            url: $(this).val(),
            method: 'GET',
            dataType: 'json',
            success: function(response) {
                const board = $('#services-board');                
                board.empty();

                $.each(response, function(index, item) {
                    const elem = $('<div class="post">');
                    elem.html(`
                        <img src="/static/img/terminal.jpg" alt="Post 1">
                        <h3>${item.title}</h3>
                        <p>${item.description}</p>
                        <p>Offered by: ${item.username}</p>
                    `);
                    board.append(elem);
                });
            },
            error: function(xhr, status, error) {
                console.error('Error fetching data:', error);
            }
        });
    });
})
