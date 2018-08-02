from thundra.opentracing.tracer import ThundraTracer


def test_trace_args(trace_args):
    tracer = ThundraTracer.getInstance()
    nodes = tracer.recorder.nodes
    count = 0
    for key in nodes:
        if key.operation_name == 'func_args':
            count += 1

    assert count == 0

    traceable_trace_args, func_args = trace_args
    func_args('arg1', arg2='arg2')

    active_span = None
    for key in nodes:
        if key.operation_name == 'func_args':
            count += 1
            active_span = key

    args = active_span.get_tag('ARGS')
    assert len(args) == 2
    assert args[0]['argValue'] == 'arg1'
    assert args[0]['argName'] == 'arg-0'
    assert args[0]['argType'] == 'str'
    assert args[1]['argValue'] == 'arg2'
    assert args[1]['argName'] == 'arg2'
    assert args[1]['argType'] == 'str'

    return_value = active_span.get_tag('RETURN_VALUE')
    assert return_value is None

    error = active_span.get_tag('thrownError')
    assert error is None

    assert count == 1
    assert traceable_trace_args.trace_args is True
    assert traceable_trace_args.trace_return_value is False
    assert traceable_trace_args.trace_error is True


def test_trace_return_values(trace_return_val):
    tracer = ThundraTracer.getInstance()
    nodes = tracer.recorder.nodes
    count = 0
    for key in nodes:
        if key.operation_name == 'func_return_val':
            count += 1

    assert count == 0

    traceable_trace_return_val, func_return_val = trace_return_val
    response = func_return_val()

    active_span = None
    for key in nodes:
        if key.operation_name == 'func_return_val':
            count += 1
            active_span = key

    args = active_span.get_tag('ARGS')
    assert args is None

    return_value = active_span.get_tag('RETURN_VALUE')
    assert return_value['returnValueType'] == type(response).__name__
    assert return_value['returnValue'] == response

    error = active_span.get_tag('thrownError')
    assert error is None

    assert count == 1
    assert traceable_trace_return_val.trace_args is False
    assert traceable_trace_return_val.trace_return_value is True
    assert traceable_trace_return_val.trace_error is True


def test_trace_error(trace_error):
    tracer = ThundraTracer.getInstance()
    nodes = tracer.recorder.nodes
    count = 0
    for key in nodes:
        if key.operation_name == 'func_with_error':
            count += 1

    assert count == 0

    traceable, func_with_error = trace_error
    try:
        func_with_error()
    except:
        active_span = None
        for key in nodes:
            if key.operation_name == 'func_with_error':
                count += 1
                active_span = key

        args = active_span.get_tag('ARGS')
        assert args is None

        return_value = active_span.get_tag('RETURN_VALUE')
        assert return_value is None

        thrown_error = active_span.get_tag('thrownError')
        assert thrown_error == 'Exception'

        assert count == 1
        assert traceable.trace_args is False
        assert traceable.trace_return_value is False
        assert traceable.trace_error is True


def test_trace_with_default_configs(trace):
    tracer = ThundraTracer.getInstance()
    nodes = tracer.recorder.nodes
    count = 0
    for key in nodes:
        if key.operation_name == 'func':
            count += 1

    assert count == 0

    traceable, func = trace
    func(arg='test')

    active_span = None
    for key in nodes:
        if key.operation_name == 'func':
            count += 1
            active_span = key

    args = active_span.get_tag('ARGS')
    assert args is None

    return_value = active_span.get_tag('RETURN_VALUE')
    assert return_value is None

    error = active_span.get_tag('thrownError')
    assert error is None

    assert count == 1
    assert traceable.trace_args is False
    assert traceable.trace_return_value is False
    assert traceable.trace_error is True

