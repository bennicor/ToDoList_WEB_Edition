from marshmallow import Schema, fields


# Схема для сериализации запросов из строки поиска
class TaskSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    done = fields.Bool()
    priority = fields.Int()
