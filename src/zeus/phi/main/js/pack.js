ctrlPack.check = function (robot) {
    if (wamp === undefined) {
        ctrlLog.log('system', 'Not connected to server!', 3);
        return false;
    }

    if (!state[robot].connected) {
        ctrlLog.log('system', 'Robot ' + robot + ' is not connected!', 3);
        return false;
    }

    return true;
};

ctrlPack.basicCall = function (robot, name) {
    if (!ctrlPack.check(robot)) {
        return;
    }

    var fn = name + '()';

    wamp.call(robot + '.' + name).then(
        function (res) {
            if (res) {
                ctrlLog.log('system', 'Executed ' + fn + '.', 1);
            } else {
                ctrlLog.log('system', 'Unable to execute ' + fn + '.', 2);
            }
        },
        function (err) {
            var message = err.args[0];
            message = message.capitalizeFirstLetter();
            ctrlLog.log('system', message + '.', 3);
        }
    )
};

ctrlPack.streams = {};

ctrlPack.registerStream = function (robot) {
    var query = $('.feed[data-name="' + robot + '"]');

    var feed = {};
    ctrlPack.streams[robot] = feed;

    feed.play = false;
    feed.changeStream = function () {
        feed.play = !feed.play;
        feed.get();
    };
    feed.get = function () {
        if (!state[robot].connected || wamp === undefined) {
            ctrlLog.log(robot, 'Unable to start video stream. Not connected.', 2);
            feed.play = false;
        }
        else if (feed.play) {
            wamp.call(robot + '.' + 'get_frame').then(
                function (res) {
                    query.find('img').attr('src', res);
                    setTimeout(feed.get, 500);
                }
            );
        }
    };

    rivets.bind(query, $.extend({feed: feed}, bindings));
};

ctrlPack.stopStream = function (robot) {
    ctrlPack.streams[robot].play = false;
};

ctrlPack.setVector = function (robot) {
    if (!ctrlPack.check(robot)) {
        return;
    }

    var v1 = state[robot].v1;
    var v2 = state[robot].v2;

    wamp.call(robot + '.' + 'set_vector', [v1, v2]).then(
        function (res) {
            if (!res) {
                ctrlLog.log('system', 'Unable to set vector.');
            }
        },
        function (err) {
            var message = err.args[0];
            message = message.capitalizeFirstLetter();
            ctrlLog.log('system', message + '.', 3);
        }
    );
};

ctrlPack.setHead = function (robot) {
    if (!ctrlPack.check(robot)) {
        return;
    }

    var p1 = state[robot].p1;
    var p2 = state[robot].p2;

    wamp.call(robot + '.' + 'set_vector', [p1, p2]).then(
        function (res) {
            if (!res) {
                ctrlLog.log('system', 'Unable to set position.');
            }
        },
        function (err) {
            var message = err.args[0];
            message = message.capitalizeFirstLetter();
            ctrlLog.log('system', message + '.', 3);
        }
    );
};

ctrlPack.pack1.stop = function () {
    ctrlPack.basicCall('pack1', 'stop');
};

ctrlPack.pack1.centerHead = function () {
    ctrlPack.basicCall('pack1', 'center_head');
};

ctrlPack.pack1.pushup = function () {
    ctrlPack.basicCall('pack1', 'pushup');
};

ctrlPack.pack1.watch = function () {
    ctrlPack.basicCall('pack1', 'watch');
};

ctrlPack.pack1.zero = function () {
    ctrlPack.basicCall('pack1', 'zero');
};

ctrlPack.pack1.bind = function () {
    ctrlPack.bindKeys('pack1');
    state.bind.active = 'pack1';
};

ctrlPack.unbindKeys = function () {
    $(document).unbind('keydown');
    ctrlLog.log('system', 'Unbinded keys.', 1);
};

ctrlPack.bindKeys = function (robot) {
    $(document).unbind('keydown');

    $(document).keydown(function(e) {
        var v = 0.5;
        var r = 0.08;
        var h = 1;

        var v1 = parseFloat(state[robot].v1);
        var v2 = parseFloat(state[robot].v2);
        var p1 = parseFloat(state[robot].p1);
        var p2 = parseFloat(state[robot].p2);

        switch (e.which) {
            case 87:
                // W key. Go forward.
                v1 += v;
                break;
            case 83:
                // S key. Go backward.
                v1 -= v;
                break;
            case 65:
                // A key. Turn left.
                v2 += r;
                break;
            case 68:
                // D key. Turn right.
                v2 -= r;
                break;
            case 37:
                // Left arrow key. Head turn left.
                p1 += h;
                break;
            case 39:
                // Right arrow key. Head turn right.
                p1 -= h;
                break;
            case 38:
                // Up arrow key. Head up.
                p2 += h;
                break;
            case 40:
                // Down arrow key. Head down.
                p2 -= h;
                break;
            default:
                return;
        }

        // Round.
        v1 = v1.toFixed(1);
        v2 = v2.toFixed(2);
        p1 = p1.toFixed(0);
        p2 = p2.toFixed(0);

        if (Math.abs(v1) < 0.001) {
            // Fix floating point error.
            v1 = 0;
        }

        if (Math.abs(v2) < 0.001) {
            // Fix floating point error.
            v2 = 0;
        }

        if (v1 !== state[robot].v1 || v2 !== state[robot].v2) {
            state[robot].v1 = v1;
            state[robot].v2 = v2;
            ctrlPack.setVector(robot, v1, v2);
        }
        else if (p1 !== state[robot].p1 || p2 !== state[robot].p2) {
            console.log('head');
            state[robot].p1 = p1;
            state[robot].p2 = p2;
            ctrlPack.setHead(robot, p1, p2);
        }
    });

    ctrlLog.log('system', 'Binded keys for robot ' + robot + '.', 1);
};

String.prototype.capitalizeFirstLetter = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
};