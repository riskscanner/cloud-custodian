import json
from c7n_tencent.client import Session
from tencentcloud.postgres.v20170312 import postgres_client, models


def merge_response(old_response, response_fist_field_name, new_response):
    """
    合并分页返回值
    @param old_response:  合并对象
    @param response_fist_field_name: 需要合并的字段
    @param new_response:   新的对象
    @return:
    """
    if not old_response:
        return new_response
    setattr(old_response, response_fist_field_name,
            getattr(old_response, response_fist_field_name) + getattr(new_response, response_fist_field_name))
    return old_response


def def_response_len_is_next_fun(old_response, new_response, response_fist_field_name, limit, total_count):
    if (len(getattr(old_response, response_fist_field_name)) if old_response else 0 + len(
            getattr(new_response, response_fist_field_name)) if new_response else 0) == getattr(new_response,
                                                                                                total_count):
        return False
    return True


def def_is_next_fun(old_response, new_response, response_fist_field_name, limit=20, total_count_field=None):
    """
    默认判断是否有下一页方法
    @param old_response:  合并的response
    @param new_response:  新的  response
    @param response_fist_field_name: 需要合并的字段
    @param limit:  每页长度
    @param total_count_field: 请求结果中 (总条数)total_count字段名
    @return:
    """
    if total_count_field:
        if not def_response_len_is_next_fun(old_response, new_response, response_fist_field_name, limit,
                                            total_count_field):
            return False
    if len(getattr(new_response, response_fist_field_name)) == limit:
        return True
    return False


def page_all(list_func, req, reponse_set_field, total_count_field=None, offset=0, limit=20, old_response=None,
             is_next_fun=def_is_next_fun):
    """
    分页查询所有数据
    @param list_func: 查询分页函数
    @param reponse_set_field 返回参数数组字段名称
    @param total_count_field 返回总数名称
    @param req       请求参数
    @param offset:    偏移量
    @param limit:     每页长度
    @param old_response: 合并的response
    @param is_next_fun: 判断是否有下一页
    @return:
    """

    params = {
        "Offset": offset,
        "Limit": limit
    }
    req.from_json_string(json.dumps(params))
    respose = list_func(req)
    old_response = merge_response(old_response, reponse_set_field, respose)
    if is_next_fun(old_response, respose, reponse_set_field, limit, total_count_field):
        return page_all(list_func, offset + 1, limit, old_response, is_next_fun)
    return old_response


if __name__ == '__main__':
    lsb = Session('AKID65nHX08TO3UZWPPtMchfZEdmrj3A9iHi', 'MXVF2iDZbOzNYVII5nsjtpvBCVZPzbaX', 'ap-shanghai').client(
        'postgres_client')
    req = models.DescribeDBInstancesRequest()
    res = page_all(lsb.DescribeDBInstances, req, 'DBInstanceSet', 'TotalCount');
    print(res)
