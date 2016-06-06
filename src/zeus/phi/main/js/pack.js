ctrlPack.check = function (robot) {
    if (wamp === undefined || !state[robot].connected) {
        ctrlLog.log(robot, 'Not connected to server!', 3);
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
                ctrlLog.log(robot, 'Executed ' + fn + '.', 1);
            } else {
                ctrlLog.log(robot, 'Unable to execute ' + fn + '.', 2);
            }
        },
        function (err) {
            ctrlPack.logError(robot, err);
        }
    )
};

ctrlPack.logError = function (robot, err) {
    var message = err.args[0];
    message = message.capitalizeFirstLetter();
    ctrlLog.log(robot, message + '.', 3);
};

ctrlPack.streams = {};

ctrlPack.registerStream = function (robot) {
    var query = $('.feed[data-name="' + robot + '"]');
    var image = query.find('img');

    var feed = {};
    ctrlPack.streams[robot] = feed;

    feed.play = false;
    feed.changeStream = function () {
        feed.play = !feed.play;
        feed.get();
    };
    feed.get = function () {
        if (!state[robot].connected || wamp === undefined || !state[robot].ip) {
            ctrlLog.log(robot, 'Unable to start video stream. Not connected.', 2);
            feed.play = false;
        }
        else if (feed.play) {
            var url = 'https://' + state[robot].ip + ':27182/?' + new Date().getTime();

            // Other method is slightly hacky.
            image.off('load');
            image.on('load', function () {
                setTimeout(feed.get, 100);
            });

            image.attr('src', url);
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

    var v1 = parseFloat(state[robot].direct.v1);
    var v2 = parseFloat(state[robot].direct.v2);

    wamp.call(robot + '.' + 'set_vector', [v1, v2]).then(
        function (res) {
            if (!res) {
                ctrlLog.log(robot, 'Unable to set vector.', 2);
            }
        },
        function (err) {
            ctrlPack.logError(robot, err);
        }
    );
};

ctrlPack.setHead = function (robot) {
    if (!ctrlPack.check(robot)) {
        return;
    }

    var p1 = parseFloat(state[robot].direct.p1);
    var p2 = parseFloat(state[robot].direct.p2);

    wamp.call(robot + '.' + 'set_head', [p1, p2]).then(
        function (res) {
            if (!res) {
                ctrlLog.log(robot, 'Unable to set head.', 2);
            }
        },
        function (err) {
            ctrlPack.logError(robot, err);
        }
    );
};

ctrlPack.liftLeg = function (robot) {
    if (!ctrlPack.check(robot)) {
        return;
    }

    var leg = parseInt(state[robot].lift.leg);
    var t = parseFloat(state[robot].lift.t);
    var height = parseFloat(state[robot].lift.height);

    wamp.call(robot + '.' + 'lift_leg', [leg, height, t]).then(
        function (res) {
            if (res) {
                ctrlLog.log(robot, 'Lifted leg ' + leg + '.', 1);
            } else {
                ctrlLog.log(robot, 'Unable to lift leg.', 2);
            }
        },
        function (err) {
            ctrlPack.logError(robot, err);
        }
    );
};

ctrlPack.targetPoint = function (robot) {
    if (!ctrlPack.check(robot)) {
        return;
    }

    var leg = parseInt(state[robot].target.leg);
    var t = parseFloat(state[robot].target.t);
    var x = parseFloat(state[robot].target.x);
    var y = parseFloat(state[robot].target.y);
    var z = parseFloat(state[robot].target.z);

    var text = [x, y, z].join(', ');

    wamp.call(robot + '.' + 'target_point', [leg, x, y, z, t]).then(
        function (res) {
            if (res) {
                ctrlLog.log(robot, 'Moved leg ' + leg + ' to (' + text + ').', 1);
            } else {
                ctrlLog.log(robot, 'Unable to move leg.', 2);
            }
        },
        function (err) {
            ctrlPack.logError(robot, err);
        }
    );
};

ctrlPack.readRFID = function (robot) {
    if (!ctrlPack.check(robot)) {
        return;
    }

    wamp.call(robot + '.' + 'read_rfid').then(
        function (res) {
            if (res) {
                ctrlLog.log(robot, 'Last read RFID is ' + res + '.', 1);
            } else {
                ctrlLog.log(robot, 'No RFID in buffer.', 2);
            }
        },
        function (err) {
            ctrlPack.logError(robot, err);
        }
    );
};

ctrlPack.emergency = function (robot) {
    if (!ctrlPack.check(robot)) {
        return;
    }

    wamp.call(robot + '.' + 'emergency').then(
        function (res) {
            if (res) {
                ctrlLog.log(robot, 'Emergency break executed.', 1);
            } else {
                ctrlLog.log(robot, 'Unable to execute emergency break.', 2);
            }
        },
        function (err) {
            ctrlPack.logError(robot, err);
        }
    );
};

ctrlPack.unbindKeys = function () {
    $(document).unbind('keydown');
    state.bind.active = null;
    ctrlLog.log('system', 'Unbinded keys.', 1);
};

ctrlPack.bindKeys = function (robot) {
    $(document).unbind('keydown');

    $(document).keydown(function(e) {
        var v = 0.5;
        var r = 0.08;
        var h = 2;

        var v1 = parseFloat(state[robot].direct.v1);
        var v2 = parseFloat(state[robot].direct.v2);
        var p1 = parseFloat(state[robot].direct.p1);
        var p2 = parseFloat(state[robot].direct.p2);

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
            case 74:
                // J. Head turn left.
                p1 += h;
                break;
            case 76:
                // L. Head turn right.
                p1 -= h;
                break;
            case 73:
                // I. Head up.
                p2 += h;
                break;
            case 75:
                // K. Head down.
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

        if (v1 !== state[robot].direct.v1 || v2 !== state[robot].direct.v2) {
            state[robot].direct.v1 = v1;
            state[robot].direct.v2 = v2;
            ctrlPack.setVector(robot);
        }
        else if (p1 !== state[robot].direct.p1 || p2 !== state[robot].direct.p2) {
            console.log('head');
            state[robot].direct.p1 = p1;
            state[robot].direct.p2 = p2;
            ctrlPack.setHead(robot);
        }
    });

    ctrlLog.log('system', 'Binded keys for robot ' + robot + '.', 1);
};

String.prototype.capitalizeFirstLetter = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
};


// Pack 1.

ctrlPack.pack1.zeroMotion = function () {
    state.pack1.direct.v1 = 0;
    state.pack1.direct.v2 = 0;
    ctrlPack.setVector('pack1');
};

ctrlPack.pack1.zeroHead = function () {
    state.pack1.direct.p1 = 0;
    state.pack1.direct.p2 = 0;
    ctrlPack.setHead('pack1');
};

ctrlPack.pack1.stop = function () {
    ctrlPack.basicCall('pack1', 'stop');
};

ctrlPack.pack1.setVector = function () {
    ctrlPack.setVector('pack1');
};

ctrlPack.pack1.setHead = function () {
    ctrlPack.setHead('pack1');
};

ctrlPack.pack1.pushup = function () {
    ctrlPack.basicCall('pack1', 'pushup');
};

ctrlPack.pack1.startWatch = function () {
    ctrlPack.basicCall('pack1', 'start_watch');
};

ctrlPack.pack1.zero = function () {
    ctrlPack.basicCall('pack1', 'zero');
};

ctrlPack.pack1.bind = function () {
    ctrlPack.bindKeys('pack1');
    state.bind.active = 'pack1';
};

ctrlPack.pack1.readRFID = function () {
    ctrlPack.readRFID('pack1');
};

ctrlPack.pack1.liftLeg = function () {
    ctrlPack.liftLeg('pack1');
};

ctrlPack.pack1.targetPoint = function () {
    ctrlPack.targetPoint('pack1');
};

ctrlPack.pack1.emergency = function () {
    ctrlPack.emergency('pack1');
};


// Pack 2.

ctrlPack.pack2.zeroMotion = function () {
    state.pack2.direct.v1 = 0;
    state.pack2.direct.v2 = 0;
    ctrlPack.setVector('pack2');
};

ctrlPack.pack2.zeroHead = function () {
    state.pack2.direct.p1 = 0;
    state.pack2.direct.p2 = 0;
    ctrlPack.setHead('pack2');
};

ctrlPack.pack2.stop = function () {
    ctrlPack.basicCall('pack2', 'stop');
};

ctrlPack.pack2.setVector = function () {
    ctrlPack.setVector('pack2');
};

ctrlPack.pack2.setHead = function () {
    ctrlPack.setHead('pack2');
};

ctrlPack.pack2.pushup = function () {
    ctrlPack.basicCall('pack2', 'pushup');
};

ctrlPack.pack2.startWatch = function () {
    ctrlPack.basicCall('pack2', 'start_watch');
};

ctrlPack.pack2.zero = function () {
    ctrlPack.basicCall('pack2', 'zero');
};

ctrlPack.pack2.bind = function () {
    ctrlPack.bindKeys('pack2');
    state.bind.active = 'pack2';
};

ctrlPack.pack2.readRFID = function () {
    ctrlPack.readRFID('pack2');
};

ctrlPack.pack2.liftLeg = function () {
    ctrlPack.liftLeg('pack2');
};

ctrlPack.pack2.targetPoint = function () {
    ctrlPack.targetPoint('pack2');
};

ctrlPack.pack2.emergency = function () {
    ctrlPack.emergency('pack2');
};