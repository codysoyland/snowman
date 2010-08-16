var conf = require('wilson').conf,
    settings = conf.settings,
    primary = conf.primary,
    app = conf.app,
    path = require('path');

settings.extend({
    'pieshop':{
        'values':{
            'DB_HOST':'localhost',
            'DB_NAME':'repocracy',
            'DB_USER':'postgres',
        },
        'addons':{
            'backend':'postpie.backends:PostgresBackend',
            'transport':'postpie.transports:PostgresTransport',
        },
    },
    'wilson':{
        'values':{
            'apps':{
                'repo':app('./repo'),
            },
            'root_urlconf':'urls.patterns',
            'middleware':[],
        }
    },
});
