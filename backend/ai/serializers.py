from rest_framework import serializers


class ChatRequestSerializer(serializers.Serializer):
    """
    Incoming chat request from React.
    """

    question = serializers.CharField(
        max_length=2000,
        help_text="The user's natural language question.",
    )

    conversation_history = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
        help_text="Previous messages for context.",
    )


class ChatResponseSerializer(serializers.Serializer):
    """
    Response returned to React.
    """

    response     = serializers.CharField()
    tools_used   = serializers.ListField(child=serializers.CharField())
    tool_results = serializers.ListField(child=serializers.DictField())
    success      = serializers.BooleanField() 