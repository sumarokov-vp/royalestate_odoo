import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    _init_districts(env)
    _init_sources(env)


def _init_districts(env):
    districts = [
        {"name": "Алатауский", "code": "alatau"},
        {"name": "Алмалинский", "code": "almaly"},
        {"name": "Ауэзовский", "code": "auezov"},
        {"name": "Бостандыкский", "code": "bostandyk"},
        {"name": "Жетысуский", "code": "zhetysu"},
        {"name": "Медеуский", "code": "medeu"},
        {"name": "Наурызбайский", "code": "nauryzbay"},
        {"name": "Турксибский", "code": "turksib"},
    ]
    District = env["estate.district"]
    for data in districts:
        if not District.search([("code", "=", data["code"])], limit=1):
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
