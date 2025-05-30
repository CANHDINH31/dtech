from mongoengine import Document, StringField

class User(Document):
    name = StringField(required=True)
    email = StringField(required=True)