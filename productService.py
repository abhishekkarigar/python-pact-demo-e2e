from bottle import route, response, run, request
@route('/builds/<buildno>',method='GET')
def getbuild(buildno):
    response.content_type='application/json'
    response.status=200
    true = True
    # the mock-consumer(pact-verifier) will initiate the Expected Request
    # the following is the actual response from this provider APP to mock-consumer(pact-verifier command )
    # now this Response will be validated with the pact file in broker_url
    return {"name": "#345","completed": true,"info": {"coverage": 30,"apiversion": 0.1,"swaggerlink": "http://swagger","buildtime": 230}}


@route('/api/_pact/state',method='POST')
def state():
    response.content_type="application/json"
    response.status=200
    return {"consumer": 'Consumer', 'state':'build 3455 exists','states':['build 3455 exists']}

run(host='localhost',port=3001)