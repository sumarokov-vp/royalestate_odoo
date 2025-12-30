# Интеграции

## Архитектура системы

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Odoo CRM       │────▶│  Royal Estate   │◀────│  ERP (Telegram) │
│  (сделки)       │     │  (объекты)      │     │  (зарплаты)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                        ┌──────┴──────┐
                        ▼             ▼
                 ┌───────────┐ ┌───────────┐
                 │ S3 Storage│ │   2GIS    │
                 │ (фото)    │ │ (карты)   │
                 └───────────┘ └───────────┘
```

---

## 1. CRM Odoo

### Связь объекта со сделкой

Объект недвижимости связывается со сделкой через поле `crm_lead_id`:

```python
class EstateProperty(models.Model):
    _name = "estate.property"

    crm_lead_id = fields.Many2one(
        'crm.lead',
        string="Сделка",
        tracking=True
    )
```

### Автоматическое создание сделки

При переходе объекта в стадию "Задаток" автоматически создаётся сделка в CRM:

```python
@api.onchange('state')
def _onchange_state_create_lead(self):
    if self.state == 'deposit' and not self.crm_lead_id:
        lead = self.env['crm.lead'].create({
            'name': f"Сделка: {self.name}",
            'partner_id': self.owner_id.id,
            'expected_revenue': self.price,
            'user_id': self.user_id.id,
        })
        self.crm_lead_id = lead.id
```

---

## 2. ERP (Telegram бот)

### API эндпоинты

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/v1/properties` | Список объектов |
| GET | `/api/v1/properties/{id}` | Детали объекта |
| POST | `/api/v1/properties/{id}/stage` | Изменить стадию |
| GET | `/api/v1/agents/{id}/properties` | Объекты агента |
| GET | `/api/v1/stats/deals` | Статистика сделок |

### Авторизация

API использует токен-авторизацию:

```
Authorization: Bearer <api_token>
```

Токен генерируется в настройках модуля Royal Estate.

### Пример запроса

```bash
curl -X GET "https://odoo.example.com/api/v1/properties?state=deal" \
  -H "Authorization: Bearer abc123" \
  -H "Content-Type: application/json"
```

### Пример ответа

```json
{
  "count": 2,
  "properties": [
    {
      "id": 1,
      "name": "2-комн. квартира, 48 м²",
      "price": 48000000,
      "state": "deal",
      "user_id": 5,
      "user_name": "Иванов Пётр",
      "deal_date": "2025-01-15"
    }
  ]
}
```

### События для ERP

При изменении состояния объекта отправляется webhook:

| Событие | Когда | Данные |
|---------|-------|--------|
| `property.sold` | Объект продан | property_id, price, user_id, commission |
| `property.assigned` | Назначен агент | property_id, old_user_id, new_user_id |
| `property.created` | Создан объект | property_id, user_id |

```python
def _trigger_webhook(self, event, data):
    """Отправить событие в ERP"""
    webhook_url = self.env['ir.config_parameter'].get_param('erp.webhook_url')
    if webhook_url:
        requests.post(webhook_url, json={
            'event': event,
            'timestamp': fields.Datetime.now().isoformat(),
            'data': data
        })
```

---

## 3. 2GIS

### Виджет карты

В форме объекта отображается виджет 2GIS с меткой на карте:

```xml
<field name="map_widget" widget="estate_2gis_map"/>
```

### Геокодирование

При сохранении адреса автоматически определяются координаты:

```python
def _compute_coordinates(self):
    """Получить координаты по адресу через 2GIS API"""
    api_key = self.env['ir.config_parameter'].get_param('2gis.api_key')
    address = f"{self.street} {self.house_number}, Алматы"

    response = requests.get(
        "https://catalog.api.2gis.com/3.0/items/geocode",
        params={'q': address, 'key': api_key}
    )

    if response.ok:
        data = response.json()
        if data.get('result', {}).get('items'):
            point = data['result']['items'][0]['point']
            self.latitude = point['lat']
            self.longitude = point['lon']
```

### Поля координат

```python
latitude = fields.Float(string="Широта", digits=(10, 7))
longitude = fields.Float(string="Долгота", digits=(10, 7))
```

---

## 4. S3 Storage (фото)

### Архитектура

```
Загрузка фото
     │
     ▼
┌─────────────┐
│ Odoo        │──────▶ Миниатюра (Binary, 300x200)
│ Controller  │
└─────────────┘
     │
     ▼
┌─────────────┐
│ S3 Storage  │──────▶ Оригинал (до 10 МБ)
└─────────────┘
```

### Модель `estate.property.image`

| Поле | Тип | Описание |
|------|-----|----------|
| `property_id` | Many2one | Связь с объектом |
| `thumbnail` | Binary | Миниатюра 300x200 |
| `s3_url` | Char | URL оригинала в S3 |
| `s3_key` | Char | Ключ объекта в S3 |
| `sequence` | Integer | Порядок сортировки |
| `is_main` | Boolean | Главное фото |

### Загрузка фото

```python
import boto3
from PIL import Image
import io

def upload_image(self, image_data):
    """Загрузить фото в S3 и создать миниатюру"""
    s3 = boto3.client('s3',
        endpoint_url=self.env['ir.config_parameter'].get_param('s3.endpoint'),
        aws_access_key_id=self.env['ir.config_parameter'].get_param('s3.access_key'),
        aws_secret_access_key=self.env['ir.config_parameter'].get_param('s3.secret_key'),
    )

    # Генерируем уникальный ключ
    s3_key = f"properties/{self.property_id.id}/{uuid.uuid4()}.jpg"

    # Загружаем оригинал в S3
    s3.put_object(
        Bucket='royal-estate',
        Key=s3_key,
        Body=image_data,
        ContentType='image/jpeg'
    )

    # Создаём миниатюру
    img = Image.open(io.BytesIO(image_data))
    img.thumbnail((300, 200))
    thumb_buffer = io.BytesIO()
    img.save(thumb_buffer, format='JPEG')

    self.write({
        's3_key': s3_key,
        's3_url': f"https://s3.example.com/royal-estate/{s3_key}",
        'thumbnail': base64.b64encode(thumb_buffer.getvalue()),
    })
```

### Водяные знаки

При экспорте фото накладывается водяной знак:

```python
def get_watermarked_image(self):
    """Получить фото с водяным знаком"""
    # Скачиваем оригинал из S3
    original = self._download_from_s3()

    # Накладываем водяной знак
    img = Image.open(io.BytesIO(original))
    watermark = Image.open('static/watermark.png')
    img.paste(watermark, (10, 10), watermark)

    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    return buffer.getvalue()
```

---

## 5. Матчинг (планируется)

### Концепция

Внешний сервис для автоматического подбора объектов под потребности покупателей.

### Потребность покупателя

```json
{
  "deal_type": "sale",
  "property_type": "apartment",
  "price_min": 30000000,
  "price_max": 50000000,
  "rooms_min": 2,
  "districts": ["medeu", "bostandyk"],
  "must_have": ["parking", "not_first_floor"]
}
```

### API матчинга

```
POST /api/v1/match
{
  "buyer_requirements": {...},
  "limit": 10
}

Response:
{
  "matches": [
    {"property_id": 123, "score": 0.95},
    {"property_id": 456, "score": 0.87}
  ]
}
```

### Интеграция с CRM

Результаты матчинга отображаются в карточке сделки (crm.lead) как рекомендуемые объекты.
