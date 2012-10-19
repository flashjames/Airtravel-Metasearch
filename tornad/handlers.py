import tornado.ioloop
import tornado.web
from tornado import httpclient
import json
from tornad.tools import parse_xml, create_url
from tornad.database import *

#django imports
from django.conf import settings
from core.models import Airports
from django.conf import settings
from django.db.models import Q

class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "".join(['POST','GET','OPTIONS', 'PUT', 'DELETE']))

class TripsHandler(BaseHandler):
   
    @tornado.web.asynchronous
    def get(self):
        print self.request.arguments
        #print test
        if not USE_LOCAL_XML:
            http = httpclient.AsyncHTTPClient()

            http.fetch(create_url("http://www.ticket.se/internal/cache/search/air",{"tripType":"ROUNDTRIP", "departureIata":"CPH", "arrivalIata":"NCE", "departureDate":"2012-11-01", "returnDate":"2012-11-06", "ticketType":"ECONOMY", "adults":"1", "children":"0", "infants":"0", "source":"zanox"}),
                       callback=self.on_response)
        else:
            self.on_response("fake-response")
        
    def on_response(self, response):
        db.trip.trips.remove()
        if not USE_LOCAL_XML:
            # TODO: Should LOG this
            if response.error:
                raise tornado.web.HTTPError(500)
            parse_xml(response.body)
        else:
             parse_xml(response)
             
        self.on_parsing_done()

    def on_parsing_done(self):
        data = db.trip.trips.find().sort('total_price',1)
        data = list(data)
        for d in data:
            if '_id' in d:
                d['_id'] = str(d['_id'])
                
        self.write(json.dumps(data))
        self.finish()

class AirportsHandler(BaseHandler):
    def get(self):
        from django.utils import simplejson
        query = self.get_argument("q")
        airports = Airports.objects.all().filter(Q(iata__istartswith=query) |
                                                 Q(airport_name__istartswith=query) |
                                                 Q(city__istartswith=query) |
                                                 Q(country__istartswith=query)
                                                 ).values('airport_name', 'country', 'iata', 'city')[0:10]
        airports_formatted = []
        for airport in airports:
            airport_formatted = "".join([airport['iata'], " - ", airport['airport_name'], " - ",
                                        airport['city'], " - ", airport['country']])
            airports_formatted.append(airport_formatted)
        import json
        #self.write(airports_formatted)
        self.write(json.dumps(airports_formatted))

