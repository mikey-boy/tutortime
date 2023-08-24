const trigger = document.querySelector('.popout-trigger');
const popoutBox = document.getElementById('popout');

trigger.addEventListener('click', function(event) {
    event.preventDefault();
    if (popoutBox.style.display == 'none')
        popoutBox.style.display = 'block';
    else
        popoutBox.style.display = 'none'
});
