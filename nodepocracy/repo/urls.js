var escaperoute = require('escaperoute'),
    routes = escaperoute.routes,
    url = escaperoute.url,
    surl = escaperoute.surl,
    sys = require('sys');

exports.patterns = routes('',
    surl('repos/([:d:w/\\-_\\.]+)/$', function(req, response, slug) {
        this.models.Repository.objects.filter({'slug__exact':slug}).all(function(objects, err) {
            if(err) {
                response.writeHead(404, {'Content-Type':'text/html'});
            } else {
                response.writeHead(200, {'Content-Type':'text/html'});
            }
            response.end();
        });
    }, 'repo_detail'),
    surl('status/([:d]+)/$', function(req, response, pk) {
        this.models.Repository.objects.filter({'pk__exact':parseInt(pk, 10)}).all(function(objects, err) {
            sys.debug(sys.inspect(objects));
            if(err || objects.length < 1) {
                response.writeHead(404, {'Content-Type':'application/json'});
            } else {
                response.writeHead(200, {'Content-Type':'text/html'});
                response.write(JSON.stringify({
                    'repo_url':objects[0].get_absolute_url(),
                    'status':objects[0].status,
                    'responder':'lovingly provided by node.js <3'
                }));
            }
            response.end();
        });
    }, 'repo_status')
);
