from tastypie import authorization
from tastypie_mongoengine import resources

import bson
import mongoengine

class Trip(mongoengine.Document):
    meta = {
        'allow_inheritance': False,
        'collection': 'trips',
    }
    currency = mongoengine.StringField()
    outbound = mongoengine.DictField()
    inbound = mongoengine.DictField()
    total_price = mongoengine.StringField(db_field="total-price")
    deeplink = mongoengine.StringField()
    
class DocumentResource(resources.MongoEngineResource):
    class Meta:
        queryset = Trip.objects.order_by('total-price')
        allowed_methods = ('get')
        authorization = authorization.Authorization()
        #collection = "test_collection" # collection name
        resource_name = "trips"


from external_apis.models import Airports
from tastypie.resources import ModelResource

class AirportResource(ModelResource):
    class Meta:
        resource_name = 'airports'
        queryset = Airports.objects.all()
        #excludes = ['user']
        allowed_methods = ['get']
        limit = 50
        #max_limit = 0
