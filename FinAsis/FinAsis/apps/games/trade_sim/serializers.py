from rest_framework import serializers
from .models import City, Character, Quest, CharacterQuest, Tournament, TournamentEntry, GameNotification, ChatMessage

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'description', 'sectors', 'market_size', 'coordinates', 'neighbors', 'sector_markets', 'weather', 'time_of_day']

class CharacterSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    city = CitySerializer(read_only=True)
    city_id = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), source='city', write_only=True, required=False)

    class Meta:
        model = Character
        fields = ['id', 'user', 'name', 'city', 'city_id', 'skills', 'story_state', 'choices', 'score', 'level', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class QuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quest
        fields = ['id', 'name', 'description', 'quest_type', 'requirements', 'rewards', 'is_active']

class CharacterQuestSerializer(serializers.ModelSerializer):
    quest = QuestSerializer(read_only=True)
    quest_id = serializers.PrimaryKeyRelatedField(queryset=Quest.objects.all(), source='quest', write_only=True)
    class Meta:
        model = CharacterQuest
        fields = ['id', 'character', 'quest', 'quest_id', 'progress', 'is_completed', 'started_at', 'completed_at']
        read_only_fields = ['id', 'character', 'quest', 'started_at', 'completed_at']

class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ['id', 'name', 'description', 'start_time', 'end_time', 'prize_pool', 'is_active', 'created_at']

class TournamentEntrySerializer(serializers.ModelSerializer):
    tournament = TournamentSerializer(read_only=True)
    tournament_id = serializers.PrimaryKeyRelatedField(queryset=Tournament.objects.all(), source='tournament', write_only=True)
    character = CharacterSerializer(read_only=True)
    character_id = serializers.PrimaryKeyRelatedField(queryset=Character.objects.all(), source='character', write_only=True)
    class Meta:
        model = TournamentEntry
        fields = ['id', 'tournament', 'tournament_id', 'character', 'character_id', 'score', 'rank', 'reward_claimed', 'joined_at']
        read_only_fields = ['id', 'tournament', 'character', 'joined_at']

class GameNotificationSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = GameNotification
        fields = ['id', 'user', 'message', 'notification_type', 'created_at', 'is_read']

class ChatMessageSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = ChatMessage
        fields = ['id', 'user', 'room', 'message', 'created_at', 'is_deleted', 'is_reported'] 