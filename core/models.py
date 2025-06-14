from mongoengine import Document, StringField, FloatField, ListField

class Question(Document):
    question = StringField(required=True)
    a = StringField(required=True)
    b = StringField(required=True)
    c = StringField(required=True)
    d = StringField(required=True)
    correct_answer = StringField(
        required=True, choices=("a", "b", "c", "d")
    )
    embedding = ListField(FloatField())
    
class ResearchDocument(Document):
    author = StringField(required=True)
    title = StringField(required=True)
    content = StringField(required=True)
    year = StringField(required=True)