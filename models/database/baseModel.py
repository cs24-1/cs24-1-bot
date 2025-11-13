from tortoise import Model


class BaseModel(Model):

    class Meta:
        abstract = True
