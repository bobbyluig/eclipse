var defaultStyle = {
    color: 0,
    name: 'EDD 2016',
    link: 'http://google.com'
};

ctrlMenu.teamSetting = function() {
    $('#team-modal')
        .modal({
            selector: {
                close: '.actions .button'
            }
        })
        .modal('show');
};

ctrlModal.teamRed = function () {
    settings.style.color = 1;
    settings.style.name = 'Eclipse Technologies';
};
ctrlModal.teamBlue = function() {
    settings.style.color = 2;
    settings.style.name = 'Paragon Industries';
};