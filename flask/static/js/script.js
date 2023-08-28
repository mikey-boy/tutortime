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
