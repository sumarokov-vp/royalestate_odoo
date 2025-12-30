import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    _init_cities(env)
    _init_districts(env)
    _init_sources(env)


def _init_cities(env):
    cities = [
        {"name": "Алматы", "code": "almaty", "sequence": 1},
    ]
    City = env["estate.city"]
    for data in cities:
        if not City.search([("code", "=", data["code"])], limit=1):
            City.create(data)
            _logger.info(f"Created city: {data['name']}")


def _init_districts(env):
    almaty = env["estate.city"].search([("code", "=", "almaty")], limit=1)
    if not almaty:
        _logger.warning("City Almaty not found, skipping districts init")
        return

    districts = [
        {"name": "Алатауский", "code": "alatau", "city_id": almaty.id},
        {"name": "Алмалинский", "code": "almaly", "city_id": almaty.id},
        {"name": "Ауэзовский", "code": "auezov", "city_id": almaty.id},
        {"name": "Бостандыкский", "code": "bostandyk", "city_id": almaty.id},
        {"name": "Жетысуский", "code": "zhetysu", "city_id": almaty.id},
        {"name": "Медеуский", "code": "medeu", "city_id": almaty.id},
        {"name": "Наурызбайский", "code": "nauryzbay", "city_id": almaty.id},
        {"name": "Турксибский", "code": "turksib", "city_id": almaty.id},
    ]
    District = env["estate.district"]
    for data in districts:
        existing = District.search([("code", "=", data["code"])], limit=1)
        if existing:
            if not existing.city_id:
                existing.write({"city_id": almaty.id})
                _logger.info(f"Updated district with city: {data['name']}")
        else:
            District.create(data)
            _logger.info(f"Created district: {data['name']}")


def _init_sources(env):
    sources = [
        {"name": "Крыша.kz", "code": "krysha", "sequence": 10},
        {"name": "OLX", "code": "olx", "sequence": 20},
        {"name": "Рекомендация", "code": "referral", "sequence": 30},
        {"name": "Холодный звонок", "code": "cold_call", "sequence": 40},
        {"name": "Вывеска", "code": "sign", "sequence": 50},
        {"name": "Соцсети", "code": "social", "sequence": 60},
        {"name": "Сайт", "code": "website", "sequence": 70},
    ]
    Source = env["estate.source"]
    for data in sources:
        if not Source.search([("code", "=", data["code"])], limit=1):
            Source.create(data)
            _logger.info(f"Created source: {data['name']}")
