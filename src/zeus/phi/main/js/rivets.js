// Configure rivets.
rivets.configure({
    templateDelimiters: ['{{', '}}']
});

rivets.formatters.eq = function(value, args) {
    return value === args;
};