import openai
from django.conf import settings
from ..models import PagePrompt, ChatSession, ChatMessage

class AIAssistant:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

    def get_page_prompt(self, page_path):
        try:
            prompt = PagePrompt.objects.get(page_path=page_path, is_active=True)
            return prompt.prompt_template
        except PagePrompt.DoesNotExist:
            return "Sen FinAsis'in yardımcı asistanısın. Kullanıcıya yardımcı olmak için buradasın."

    def generate_response(self, message, page_context, chat_history=None):
        page_prompt = self.get_page_prompt(page_context.get('path', ''))
        
        messages = [
            {"role": "system", "content": page_prompt},
        ]
        
        if chat_history:
            for msg in chat_history:
                role = "user" if msg.is_user else "assistant"
                messages.append({"role": role, "content": msg.content})
        
        messages.append({"role": "user", "content": message})
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Üzgünüm, bir hata oluştu: {str(e)}"

    def create_chat_session(self, user, page_context):
        return ChatSession.objects.create(
            user=user,
            page_context=page_context
        )

    def save_message(self, session, content, is_user=True, metadata=None):
        return ChatMessage.objects.create(
            session=session,
            content=content,
            is_user=is_user,
            metadata=metadata or {}
        ) 