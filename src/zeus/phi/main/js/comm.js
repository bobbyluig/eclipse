var defaultComm = {
    authid: 'Zeus',
    secret: '+Ew~77XrvW-c<6sZ',
    url: 'wss://192.168.193.1/ws/',
    realm: 'lycanthrope',
    authmethod: 'wampcra',
    max_retries: 15,
    initial_retry_delay: 5,
    max_retry_delay: 10,
    retry_delay_growth: 1.1
};

ctrlMenu.commSetting = function() {
    $('#comm-modal').modal('show');
};

ctrlModal.resetComm = function() {
    for(var property in settings.comm) {
        if(settings.comm.hasOwnProperty(property) && defaultComm.hasOwnProperty(property)) {
            settings.comm[property] = defaultComm[property];
        }
    }
};