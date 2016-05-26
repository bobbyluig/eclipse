ctrlPack.check = function () {
    if (wamp === undefined) {
        ctrlLog.log('system', 'Not connected to server!', 3);
        return false;
    }

    if (ctrlPack.robot != 'pack1' && ctrlPack.robot != 'pack2') {
        ctrlLog.log('system', 'Unknown robot ' + id + '.');
        return false;
    }

    return true;
};

ctrlPack.robot = 'pack1';

ctrlPack.setRobot = function (id) {
    if (id == 'one' || id == '1') {
        ctrlPack.pack1();
    }
    else if (id == 'to' || id == '2') {
        ctrlPack.pack2();
    }
};

ctrlPack.pack1 = function () {
    if (ctrlPack.robot != 'pack1') {
        ctrlPack.robot = 'pack1';
        ctrlLog.log('system', 'Controlling pack 1.', 1);
    }
};

ctrlPack.pack2 = function () {
    if (ctrlPack.robot != 'pack2') {
        ctrlPack.robot = 'pack2';
        ctrlLog.log('system', 'Controlling pack 2.', 1);
    }
};

ctrlPack.basicCall = function (name, array) {
    if (!ctrlPack.check()) {
        return false;
    }

    var fn;

    if (array === undefined) {
        fn = name + '()';
    } else {
        fn = name + '(' + array.join(', ') + ')';
    }

    wamp.call(ctrlPack.robot + '.' + name, array).then(
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

ctrlPack.setVector = function (vector) {
    ctrlPack.basicCall('set_vector', vector);
};

ctrlPack.setHead = function (position) {
    ctrlPack.basicCall('set_head', position);
};

ctrlPack.stopWatch = function () {
    ctrlPack.basicCall('stop_watch');
};

ctrlPack.centerHead = function () {
    ctrlPack.basicCall('center_head');
};

ctrlPack.pushup = function () {
    ctrlPack.basicCall('pushup');
};

ctrlPack.watch = function () {
    ctrlPack.basicCall('watch');
};

ctrlPack.zero = function () {
    ctrlPack.basicCall('zero');
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
    });

    ctrlLog.log('system', 'Binded keys.', 1);
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

String.prototype.capitalizeFirstLetter = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
};