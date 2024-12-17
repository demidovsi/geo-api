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
    cities = list()
    metrics = list()
    url = "v1/select/{schema}/nsi_import?where=object_code='cities' and " \
          " param_name in ('life_index', 'crime_index', 'health_index')".format(schema=config.SCHEMA_NAME)
    answer_metrics, is_ok, status = send_rest(url)
    if is_ok:
        answer_metrics = json.loads(answer_metrics)
        for data in answer_metrics:
            metrics.append({"metric": data['param_name'], "source": data['sh_name'], "metric_name": data['name'],
                            "url": data['code']})

    url = "v1/select/{schema}/v_nsi_cities?where=name_country='United States'".format(schema=config.SCHEMA_NAME)
    answer_cities, is_ok, status = send_rest(url)
    if is_ok:
        answer_cities = json.loads(answer_cities)
        st_id = '' # список идентификаторов городов
        for data in answer_cities:
            st_id = st_id + ', ' if st_id else st_id
            st_id += str(data['id'])
            param = {"city_id": data['id'], "city_name": data["sh_name"], "country_name": data['name_country'],
                     "population": data['population']}
            if data['name_province']:
                param['province_name'] = data['name_province']
            cities.append(param)
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
    answer = json.loads(answer)
    min_date = '2100-01-01'
    max_date = '1900-01-01'
    for data in answer:
        city_id = data['cities_id']
        date = data['dt'].split('T')[0]
        min_date = min(min_date, date)
        max_date = max(max_date, date)
        result.append({'city_id': city_id, 'date': date, 'value': data['value'], 'metric': data['param_name']})
    return {"cities_count": len(cities), "metrics_count": len(metrics), "values_count": len(result),
            "min_date": min_date, "max_date": max_date,
            "metrics": metrics, "cities": cities, "values": result}
