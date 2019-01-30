
import psycopg2
from psycopg2 import Error as PostgreError
from thundra.opentracing.tracer import ThundraTracer
from thundra import constants


def test_postgre_integration():
    query = "select 1 + 1 AS solution"

    connection =  psycopg2.connect(
        user='user',
        host='localhost',
        password='userpass',
        dbname='db')

    try:
        cursor = connection.cursor()
        cursor.execute(query)
        for table in cursor.fetchall():
            print(table)

    finally:
        tracer = ThundraTracer.get_instance()
        postgre_span = tracer.recorder.finished_span_stack[0]

        assert postgre_span.domain_name == constants.DomainNames['DB']
        assert postgre_span.class_name == constants.ClassNames['POSTGRESQL']
        assert postgre_span.operation_name == 'db'
        assert postgre_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'READ'
        assert postgre_span.get_tag(constants.SpanTags['DB_INSTANCE']) == 'db'
        assert postgre_span.get_tag(constants.SpanTags['DB_HOST']) == 'localhost'
        assert postgre_span.get_tag(constants.SpanTags['DB_STATEMENT']) == query.lower()
        assert postgre_span.get_tag(constants.SpanTags['DB_STATEMENT_TYPE']) == 'SELECT'
        assert postgre_span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'API'
        assert postgre_span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-Lambda'

        tracer.clear()
        connection.close()

def test_postgre_integration_with_empty_query():
    connection =  psycopg2.connect(
        user='user',
        host='localhost',
        password='userpass',
        dbname='db')

    try:
        cursor = connection.cursor()
        cursor.execute('')
        for table in cursor.fetchall():
            print(table)
    except PostgreError:
        pass
    finally:
        tracer = ThundraTracer.get_instance()
        postgre_span = tracer.recorder.finished_span_stack[0]

        assert postgre_span.domain_name == constants.DomainNames['DB']
        assert postgre_span.class_name == constants.ClassNames['POSTGRESQL']
        assert postgre_span.operation_name == 'db'
        assert postgre_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == ''
        assert postgre_span.get_tag(constants.SpanTags['DB_INSTANCE']) == 'db'
        assert postgre_span.get_tag(constants.SpanTags['DB_HOST']) == 'localhost'
        assert postgre_span.get_tag(constants.SpanTags['DB_STATEMENT']) == ''
        assert postgre_span.get_tag(constants.SpanTags['DB_STATEMENT_TYPE']) == ''
        assert postgre_span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'API'
        assert postgre_span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'AWS-Lambda'

        tracer.clear()
        connection.close()