from pydantic import BaseModel

try:
    from bson.objectid import ObjectId as BsonObjectId

    class PyObjectId(BsonObjectId):
        @classmethod
        def __get_validators__(cls):
            yield cls.validate

        @classmethod
        def validate(cls, v):
            if not isinstance(v, (cls, BsonObjectId, str)) or not BsonObjectId.is_valid(
                v
            ):
                raise TypeError("Invalid ObjectId.")
            return str(v)

        @classmethod
        def __modify_schema__(cls, field_schema: dict):
            field_schema.update(
                type="string",
                examples=["5eb7cf5a86d9755df3a6c593", "5eb7cfb05e32e07750a1756a"],
            )

    class _(BaseModel):
        a: PyObjectId

except:
    from ruson import PydanticObjectId as PyObjectId
