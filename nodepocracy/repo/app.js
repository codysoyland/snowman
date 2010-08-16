var wilson = require('wilson'),
    application = wilson.application,
    app = application.app,
    primary = application.primary,
    any = application.any,
    specific = application.specific;

exports.app = app({
    'provides':'repo',
    'models':require('./models'),
    'external_apps':{},
    'urls':require('./urls').patterns,
});
