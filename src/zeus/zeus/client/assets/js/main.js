// So I can type less
var app = angular.module('application');

// Configure Autobahn.
var authid = 'Zeus';
var secret = '+Ew~77XrvW-c<6sZ';
var url = 'wss://192.168.12.18/ws/';
var realm = 'lycanthrope';
var authmethod = 'wampcra';

app.config(function ($wampProvider) {
  $wampProvider.init({
    url: url,
    realm: realm,
    authmethods: [authmethod],
    authid: authid,
    max_retries: 15,
    initial_retry_delay: 5,
    max_retry_delay: 10,
    retry_delay_growth: 1.1
  });

  $wampProvider.interceptors.push('wampInterceptor');
});

// Notification controller (it's always there)
app.controller('NoteCtrl', function ($scope, $wamp, FoundationApi) {
  $scope.$on('$wamp.onchallenge', function (event, data) {
    if (data.method === authmethod) {
      return data.promise.resolve(autobahn.auth_cra.sign(secret, data.extra.challenge));
    }
  });

  $scope.$on('$wamp.open', function (event, session) {
    FoundationApi.publish('main-notifications', {
      title: 'WAMP Connection',
      content: 'Connection gained!',
      color: 'success',
      autoclose: '3000'
    });
  });

  $scope.$on('$wamp.close', function (event, data) {
    if (data.will_retry) {
      FoundationApi.publish('main-notifications', {
        title: 'WAMP Connection',
        content: 'Connection lost.',
        color: 'alert',
        autoclose: '3000'
      });
    } else {
      FoundationApi.publish('main-notifications', {
        title: 'WAMP Connection',
        content: 'No connection. Recovering.',
        color: 'warning',
        autoclose: '3000'
      });
    }
  });
});

// Button controller (temporary)
app.controller('BtnCtrl', function ($scope, $timeout, $wamp, FoundationApi, AnnyangService, SpeechService, ngAudio) {
  $scope.startWAMP = function () {
    $wamp.open();
  };

  $scope.stopMusic = function () {
    $wamp.call('zeus.stop');
  };

  $scope.stopMusicMethod = function () {
    $scope.sound.stop();
  };

  $scope.voice = 'Enable Voice';

  $scope.startAnnyang = function () {
    AnnyangService.addCommand('DOG tiger', function () {
      flex($scope, ngAudio, $wamp);
    });
    AnnyangService.addCommand('DOG walk (forward)', function () {
      $wamp.call('dog1.walk');
    });
    AnnyangService.addCommand('DOG do pushups', function () {
      $wamp.call('dog1.pushup');
    });
    AnnyangService.addCommand('DOG stop', function () {
      $wamp.call('dog1.stop');
    });
    AnnyangService.addCommand('DOG initialize', function () {
      $wamp.call('dog1.initialize');
    });
    AnnyangService.addCommand('DOG *phrase', function (phrase) {
      $wamp.call('dog1.converse', [phrase])
    });

    if (AnnyangService.isListening()) {
      AnnyangService.stop();
      $scope.voice = 'Enable Voice';
    } else {
      AnnyangService.start();
      $scope.voice = 'Disable Voice';
    }
  };

  $scope.flex = function () {
    $scope.sound = ngAudio.load('/assets/audio/tiger.mp3');
    $scope.sound.play();
    var unregister = $scope.$watch('sound.currentTime', function (time) {
      if (time >= 9.3) {
        $wamp.call('dog1.flex');
        unregister();
      }
    });
  };

  $scope.startAudio = function () {
    $wamp.subscribe('dog1.info', SpeechService.speak);
    $wamp.register('zeus.flex', $scope.flex);
    $wamp.register('zeus.stop', $scope.stopMusicMethod);
    FoundationApi.publish('main-notifications', {
      title: 'Audio',
      content: 'Audio registered!',
      color: 'success',
      autoclose: '3000'
    });
  };

  // Buttons just in case.
  $scope.dogWalk = function () {
    $wamp.call('dog1.walk');
  };
  $scope.dogPushup = function () {
    $wamp.call('dog1.pushup');
  };
  $scope.dogStop = function () {
    $wamp.call('dog1.stop');
  };
  $scope.dogInitialize = function () {
    $wamp.call('dog1.initialize');
  };
  $scope.dogFlex = function () {
    $wamp.call('zeus.flex');
  }
});

// Voice control factory
app.factory('AnnyangService', function ($rootScope) {
  var service = {};

  // Start uninitialized and off.
  service.initialized = false;

  // COMMANDS
  service.commands = {};

  service.addCommand = function (phrase, callback) {
    var command = {};

    // Wrap annyang command in scope apply
    command[phrase] = function (args) {
      $rootScope.$apply(callback(args));
    };

    // Extend our commands list
    angular.extend(service.commands, command);

    // Add the commands to annyang
    // annyang.addCommands(service.commands);
    // console.debug('Added command "' + phrase + '"', service.commands);
  };

  service.isListening = function () {
    return annyang.isListening();
  };

  service.stop = function () {
    annyang.abort();
  };

  service.start = function () {
    annyang.addCommands(service.commands);
    annyang.debug(true);
    annyang.start();
    service.initialized = true;
  };

  return service;
});

// Speech service
app.factory('SpeechService', function ($rootScope) {
  var service = [];

  service.speak = function (text) {
    if (text.constructor === Array) {
      text = text[0];
    }

    var msg = new SpeechSynthesisUtterance();
    msg.lang = 'en-US';
    msg.text = text;
    window.speechSynthesis.speak(msg);
  };

  return service;
});

// WAMP error interceptor
app.factory('wampInterceptor', function ($q, FoundationApi) {
  return {
    'callResponseError': function (response) {
      FoundationApi.publish('main-notifications', {
        title: 'WAMP Response',
        content: response.error.args[0],
        color: 'error',
        autoclose: '3000'
      });
    },
    'subscribeResponseError': function (response) {
      FoundationApi.publish('main-notifications', {
        title: 'WAMP Response',
        content: response.error.args[0],
        color: 'error',
        autoclose: '3000'
      });
    },
    'publishResponseError': function (response) {
      FoundationApi.publish('main-notifications', {
        title: 'WAMP Response',
        content: response.error.args[0],
        color: 'error',
        autoclose: '3000'
      });
    },
    'registerResponseError': function (response) {
      FoundationApi.publish('main-notifications', {
        title: 'WAMP Response',
        content: response.error.args[0],
        color: 'error',
        autoclose: '3000'
      });
    }
  };
});

// angular.element(document.body).injector().get('$wamp').call('dog1.');
