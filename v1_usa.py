import json

from fastapi import APIRouter

import common
import config
from common import send_rest

sub_v1_usa = APIRouter()


@sub_v1_usa.get('/v1/usa/his/cities', summary='Историческая информация по городам США')
def v1_usa_his_cities_get(city_id=None):
    """
    :return:
    """
    result = list()
    answer = dict()
    if city_id is None:
        url = "v1/select/{schema}/v_nsi_cities?where=name_country='United States'".format(schema=config.SCHEMA_NAME)
        answer_cities, is_ok, status = send_rest(url)
        if is_ok:
            answer_cities = json.loads(answer_cities)
            st_id = '' # список идентификаторов городов
            for data in answer_cities:
                st_id = st_id + ', ' if st_id else st_id
                st_id += str(data['id'])
            txt, is_ok, token_admin, lang_admin = common.login_superadmin()
            st = "select *, 'life_index' as param_name from {schema}.his_cities_life_index " \
                 "where cities_id in ({st_id})" \
                 " union " \
                 "select *, 'crime_index' from {schema}.his_cities_crime_index where cities_id in ({st_id})" \
                 " union " \
                 "select *, 'health_index' from {schema}.his_cities_health_index where cities_id in ({st_id});".format(
                st_id=st_id, schema=config.SCHEMA_NAME
            )
            answer, is_ok, status = send_rest('v1/execute?view=1', 'PUT', params=st, token_user=token_admin)
    # return json.dump(result, indent=4, ensure_ascii=False, sort_keys=True)
    answer = json.loads(answer)
    result = list()
    for data in answer:
        city_id = data['0']
        result.append({'city_id': city_id, 'date': data['1'], 'value': data['2'], 'param_name': data['3']})
    return result