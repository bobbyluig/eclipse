ctrlPack.check = function () {
    if (wamp === undefined) {
        ctrlLog.log('system', 'Not connected to server!', 3);
        return false;
    } else {
        return true;
    }
};

ctrlPack.getFeed = function () {
    if (!ctrlPack.check()) {
        return false;
    }

    wamp.call('pack1.get_feed')
        .then(function (res) {
            $('#feed').attr('src', res);
            ctrlLog.log('system', 'Executed get_feed().', 1);
        });
};

ctrlPack.follow = function () {
    if (!ctrlPack.check()) {
        return false;
    }

    wamp.call('pack1.follow')
        .then(function (res) {
            if (res) {
                ctrlLog.log('system', 'Executed follow().', 1);
            } else {
                ctrlLog.log('system', 'Unable to execute follow().', 3);
            }
        });
};

ctrlPack.setVector = function (vector) {
    if (!ctrlPack.check()) {
        return false;
    }

    console.log(vector);

    wamp.call('pack1.set_vector', vector)
        .then(function (res) {
            if (res) {
                var str = 'set_vector(' + vector[0].toFixed(2) + ', ' + vector[1].toFixed(2) + ')';
                ctrlLog.log('system', 'Executed ' + str + '.', 1)
            } else {
                ctrlLog.log('system', 'Unable to execute set_vector().', 3);
            }
        });
};

ctrlPack.setHead = function (position) {
    if (!ctrlPack.check()) {
        return false;
    }

    wamp.call('pack1.set_head', position)
        .then(function (res) {
            if (res) {
                var str = 'set_head(' + position[0].toFixed(2) + ', ' + position[1].toFixed(2) + ')';
                ctrlLog.log('system', 'Executed ' + str + '.', 1);
            } else {
                ctrlLog.log('system', 'Unable to execute set_head()', 3);
            }
        });
};

ctrlPack.globalStop = function () {
    if (!ctrlPack.check()) {
        return false;
    }

    wamp.call('pack1.global_stop')
        .then(function (res) {
            if (res) {
                ctrlLog.log('system', 'Executed global_stop().', 1);
            } else {
                ctrlLog.log('system', 'Unable to execute global_stop().', 3);
            }
        });
};

ctrlPack.stopWatch = function () {
    if (!ctrlPack.check()) {
        return false;
    }

    wamp.call('pack1.stop_watch')
        .then(function (res) {
            if (res) {
                ctrlLog.log('system', 'Executed stop_watch().', 1);
            } else {
                ctrlLog.log('system', 'Unable to execute stop_watch().', 3);
            }
        });
};

ctrlPack.centerHead = function () {
    if (!ctrlPack.check()) {
        return false;
    }

    wamp.call('pack1.center_head')
        .then(function (res) {
            if (res) {
                ctrlLog.log('system', 'Executed center_head().', 1);
            } else {
                ctrlLog.log('system', 'Unable to execute center_head().', 3);
            }
        });
};

ctrlPack.pushup = function () {
    if (!ctrlPack.check()) {
        return false;
    }
    
    wamp.call('pack1.pushup')
        .then(function (res) {
            if (res) {
                ctrlLog.log('system', 'Executed pushup().', 1);
            } else {
                ctrlLog.log('system', 'Unable to execute pushup().', 3);
            }
        });
};

ctrlPack.watch = function () {
    if (!ctrlPack.check()) {
        return false;
    }

    wamp.call('pack1.watch')
        .then(function (res) {
            if (res) {
                ctrlLog.log('system', 'Executed watch().', 1);
            } else {
                ctrlLog.log('system', 'Unable to execute watch().', 3);
            }
        });
};

ctrlPack.zero = function () {
    if (!ctrlPack.check()) {
        return false;
    }

    wamp.call('pack1.zero')
        .then(function (res) {
            if (res) {
                ctrlLog.log('system', 'Executed zero().', 1);
            } else {
                ctrlLog.log('system', 'Unable to execute zero().', 3);
            }
        });
};

ctrlPack.vector = [0, 0];
ctrlPack.position = [0, 0];

ctrlPack.unbindKeys = function () {
    $(document).unbind('keydown');
    ctrlLog.log('system', 'Unbinded keys.', 1);
};

ctrlPack.bindKeys = function () {
    $(document).unbind('keydown');

    $(document).keydown(function(e) {
        var v = 0.5;
        var r = 0.08;
        var h = 1;

        var vector = ctrlPack.vector.slice(0);
        var position = ctrlPack.position.slice(0);

        switch (e.which) {
            case 87:
                // W key. Go forward.
                vector[0] += v;
                break;
            case 83:
                // S key. Go backward.
                vector[0] -= v;
                break;
            case 65:
                // A key. Turn left.
                vector[1] += r;
                break;
            case 68:
                // D key. Turn right.
                vector[1] -= r;
                break;
            case 37:
                // Left arrow key. Head turn left.
                position[0] += h;
                break;
            case 39:
                // Right arrow key. Head turn right.
                position[0] -= h;
                break;
            case 38:
                // Up arrow key. Head up.
                position[1] += h;
                break;
            case 40:
                // Down arrow key. Head down.
                position[1] -= h;
                break;
        }

        if (!arraysEqual(ctrlPack.vector, vector)) {
            ctrlPack.vector = vector.slice(0);
            ctrlPack.setVector(vector);
        }

        if (!arraysEqual(ctrlPack.position, position)) {
            ctrlPack.position = position.slice(0);
            ctrlPack.setHead(position);
        }

        ctrlLog.log('system', 'Binded keys.', 1);
    });
};

function arraysEqual(a, b) {
  if (a === b) return true;
  if (a == null || b == null) return false;
  if (a.length != b.length) return false;

  // If you don't care about the order of the elements inside
  // the array, you should sort both arrays here.

  for (var i = 0; i < a.length; ++i) {
    if (a[i] !== b[i]) return false;
  }
  return true;
}