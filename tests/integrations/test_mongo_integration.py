import os
from bson.json_util import loads
from pymongo import MongoClient
from thundra import constants
from thundra.opentracing.tracer import ThundraTracer


def test_command_insert():
    client = MongoClient('localhost', 27017)
    db = client.test

    post = {"author": "Mike",
            "text": "My first blog post!",
            "tags": ["mongodb", "python", "pymongo"]}

    db.posts.insert_one(post).inserted_id
    tracer = ThundraTracer.get_instance()
    span = tracer.get_spans()[0]

    assert span.operation_name == 'INSERT'
    assert span.class_name == constants.ClassNames['MONGODB']
    assert span.domain_name == constants.DomainNames['DB']

    assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'WRITE'
    assert span.get_tag(constants.DBTags['DB_HOST']) == 'localhost'
    assert span.get_tag(constants.DBTags['DB_PORT']) == 27017
    assert span.get_tag(constants.DBTags['DB_INSTANCE']) == 'test'
    assert span.get_tag(constants.MongoDBTags['MONGODB_COMMAND_NAME']) == 'INSERT'

    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['']
    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.LAMBDA_APPLICATION_DOMAIN_NAME
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.LAMBDA_APPLICATION_CLASS_NAME
    assert span.get_tag(constants.SpanTags['TOPOLOGY_VERTEX'])

    mongo_command = loads(span.get_tag(constants.MongoDBTags['MONGODB_COMMAND']))
    assert mongo_command.get('documents')[0].get('text') == "My first blog post!"

    tracer.clear()


def test_command_update():
    client = MongoClient('localhost', 27017)
    db = client.test

    post = {"author": "Mike",
            "text": "My first blog post!",
            "tags": ["mongodb", "python", "pymongo"]}

    db.posts.insert_one(post).inserted_id
    tracer = ThundraTracer.get_instance()
    tracer.clear()

    db.posts.update_one({'author': 'Mike'}, {'$set': {'text': 'My edited blog post!'}})

    span = tracer.get_spans()[0]

    assert span.operation_name == 'UPDATE'
    assert span.class_name == constants.ClassNames['MONGODB']
    assert span.domain_name == constants.DomainNames['DB']

    assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'WRITE'
    assert span.get_tag(constants.DBTags['DB_HOST']) == 'localhost'
    assert span.get_tag(constants.DBTags['DB_PORT']) == 27017
    assert span.get_tag(constants.DBTags['DB_INSTANCE']) == 'test'
    assert span.get_tag(constants.MongoDBTags['MONGODB_COMMAND_NAME']) == 'UPDATE'

    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['']
    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.LAMBDA_APPLICATION_DOMAIN_NAME
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.LAMBDA_APPLICATION_CLASS_NAME
    assert span.get_tag(constants.SpanTags['TOPOLOGY_VERTEX'])

    mongo_command = loads(span.get_tag(constants.MongoDBTags['MONGODB_COMMAND']))
    assert mongo_command.get('updates')[0].get('q') == {'author': 'Mike'}
    assert mongo_command.get('updates')[0].get('u').get('$set') == {'text': 'My edited blog post!'}

    tracer.clear()


def test_command_failed():
    client = MongoClient('localhost', 27017)
    db = client.test

    try:
        for x in db.posts.find({}, {"field1": 1, "field2": 0}):
            print(x)
    except:
        pass

    tracer = ThundraTracer.get_instance()
    span = tracer.get_spans()[0]

    assert span.operation_name == 'FIND'
    assert span.class_name == constants.ClassNames['MONGODB']
    assert span.domain_name == constants.DomainNames['DB']

    assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'READ'
    assert span.get_tag(constants.DBTags['DB_HOST']) == 'localhost'
    assert span.get_tag(constants.DBTags['DB_PORT']) == 27017
    assert span.get_tag(constants.DBTags['DB_INSTANCE']) == 'test'
    assert span.get_tag(constants.MongoDBTags['MONGODB_COMMAND_NAME']) == 'FIND'

    assert span.get_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['']
    assert span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == constants.LAMBDA_APPLICATION_DOMAIN_NAME
    assert span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == constants.LAMBDA_APPLICATION_CLASS_NAME
    assert span.get_tag(constants.SpanTags['TOPOLOGY_VERTEX'])

    assert span.get_tag('error') == True

    tracer.clear()


def test_mongo_command_masked(monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_MASK_MONGODB_COMMAND, 'true')
    client = MongoClient('localhost', 27017)
    db = client.test
    db.list_collection_names()

    tracer = ThundraTracer.get_instance()
    span = tracer.get_spans()[0]
    assert span.get_tag(constants.MongoDBTags['MONGODB_COMMAND']) == None
    tracer.clear()