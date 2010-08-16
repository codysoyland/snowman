var escaperoute = require('escaperoute'),
    wilson = require('wilson'),
    app = wilson.urls.app,
    wrap = wilson.urls.wrap,
    routes = escaperoute.routes,
    url = escaperoute.url,
    surl = escaperoute.surl;

exports.patterns = routes('',
    // include app urls with `app`
    app('^/', 'repo')
)

