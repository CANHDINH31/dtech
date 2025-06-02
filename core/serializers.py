from rest_framework import serializers

class ResearchDocumentSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    author = serializers.CharField()
    title = serializers.CharField()
    content = serializers.CharField()
    year = serializers.CharField()
