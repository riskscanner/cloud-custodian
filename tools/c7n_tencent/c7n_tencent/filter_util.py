import jsonpath
import json
import time


def get_value(res_i, value_key):
    """
    获取数据
    @param res_i:
    @param value_key:
    @return:
    """
    json_str = json.dumps(res_i)
    u_str = json.loads(json_str)
    if str(value_key).startswith("$."):
        return jsonpath.jsonpath(u_str, value_key)
    return jsonpath.jsonpath(u_str, '$.' + value_key)


def like(filter_obj, i):
    """
    判断是否匹配
    @param filter_obj:
    @param i:
    @return:
    """
    cloud_value = get_value(i, filter_obj.schema['properties']['type']['enum'][0])
    if cloud_value:
        if len(cloud_value) == 0:
            return False
        like_value = filter_obj.data.get('like', '')
        # 如果不传入数据默认不过滤
        if like_value:
            return like_value in cloud_value[0]
        return True


def eq(filter_obj, i):
    """
    判断是否相等
    @param filter_obj:
    @param i:
    @return:
    """
    cloud_value = get_value(i, filter_obj.schema['properties']['type']['enum'][0])
    if cloud_value:
        if len(cloud_value) == 0:
            return False
        value = filter_obj.data.get('value', '')
        # 如果不传入数据默认不过滤
        if value:
            return value == cloud_value[0]
        return True


def time_to_num(time_str, format):
    # 2017-12-04 00:00:00
    print(time_str)
    timeArray = time.strptime(time_str, format)
    return int(time.mktime(timeArray))


def region(filter_obj, i):
    """
    判断是否是在某个范围
    @param filter_obj:
    @param i:
    @return:
    """
    cloud_value = get_value(i, filter_obj.schema['properties']['type']['enum'][0])
    ge = filter_obj.data.get('ge', '')
    le = filter_obj.data.get('le', '')
    if len(cloud_value) == 0:
        return False
    cloud_value = cloud_value[0]
    if cloud_value and len(str(cloud_value)) > 0 and isinstance(cloud_value, str):
        cloud_value = time_to_num(cloud_value, '%Y-%m-%d %H:%M:%S')
    # 如果不传入数据默认不过滤
    if cloud_value and (isinstance(cloud_value, int) or isinstance(cloud_value, float)):
        if ge and le:
            return ge <= cloud_value <= le
        elif ge:
            return ge <= cloud_value
        elif le:
            return cloud_value <= le
    return True


def is_null(filter_obj, i):
    """
    判断变量是否存在
    @param filter_obj:
    @param i:
    @return:
    """
    cloud_value = get_value(i, filter_obj.schema['properties']['type']['enum'][0])
    if cloud_value:
        is_empty = filter_obj.data.get('is_empty', '')
        if is_empty and len(cloud_value) == 0:
            return i
        elif not is_empty and len(cloud_value) != 0:
            return i
        else:
            return False


def in_like(filter_obj, i):
    in_like_value = filter_obj.data.get('in_like', '')
    cloud_value = get_value(i, filter_obj.schema['properties']['type']['enum'][0])
    if cloud_value:
        if isinstance(cloud_value[0], list):
            for index in range(list(cloud_value[0])):
                if in_like_value in cloud_value[0][index]:
                    return i
    else:
        False


def in_eq(filter_obj, i):
    in_value = filter_obj.data.get('in', '')
    cloud_value = get_value(i, filter_obj.schema['properties']['type']['enum'][0])
    if cloud_value:
        if isinstance(cloud_value[0], list):
            if list(cloud_value[0]).__contains__(in_value):
                return i
    else:
        False


def filter_res(filter_obj, i):
    """
    过滤返回对象
    @param filter_obj:
    @param i:
    @return:
    """
    like_value = filter_obj.data.get('like', '')
    value = filter_obj.data.get('value', '')
    ge = filter_obj.data.get('ge', '')
    le = filter_obj.data.get('le', '')
    is_empty = filter_obj.data.get('is_empty', '')
    in_like_field = filter_obj.data.get('in_like', '')
    in_eq_field = filter_obj.data.get('in', '')
    if like_value:
        if like(filter_obj, i):
            return i
        else:
            return False
    elif value:
        if eq(filter_obj, i):
            return i
        else:
            return False
    elif ge or le:
        if region(filter_obj, i):
            return i
        else:
            return False
    elif is_empty:
        if is_null(filter_obj, i):
            return i
        else:
            return False
    elif in_like_field:
        if in_like(filter_obj, i):
            return i
        else:
            return False
    elif in_eq_field:
        if in_eq(filter_obj, i):
            return i
        else:
            return False

    return i


types = {
    'is_empty': {'is_empty': {'type': 'boolean'}},
    'boolean': {'value': {'type': 'boolean'}, 'is_empty': {'type': 'boolean'}},
    'number': {'ge': {'type': 'number'}, 'le': {'type': 'number'}, 'is_empty': {'type': 'boolean'}},
    'string': {'like': {'type': 'string'}, 'value': {'type': 'string'}, 'is_empty': {'type': 'boolean'}},
    'list_string': {'in': {'type': 'string'}, 'in_like': {'type': {'type': 'string'}},
                    'is_empty': {'type': 'boolean'}},
    'list_number': {'in': {'type': 'number'}, 'in_like': {'type': 'number'}, 'is_empty': {'type': 'boolean'}},
    'time': {'ge': {'type': 'number'}, 'le': {'type': 'number'}, 'is_empty': {'type': 'boolean'}}
}


def get_schema(type):
    """
    获取类型
    @param type:
    @return:
    """
    return types.get(type)
