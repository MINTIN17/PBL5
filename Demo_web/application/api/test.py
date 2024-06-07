from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

# Tạo một chatbot mới
chatbot = ChatBot(
    'MyBot',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    logic_adapters=[
        'chatterbot.logic.MathematicalEvaluation',
        'chatterbot.logic.BestMatch'
    ],
    database_uri='sqlite:///database.sqlite3'
)

# Huấn luyện chatbot với dữ liệu mẫu
trainer = ChatterBotCorpusTrainer(chatbot)
trainer.train('chatterbot.corpus.english')

print("Chatbot đã sẵn sàng để trò chuyện!")

# Bắt đầu trò chuyện với chatbot
while True:
    try:
        user_input = input("Bạn: ")
        bot_response = chatbot.get_response(user_input)
        print(f"Bot: {bot_response}")
    except (KeyboardInterrupt, EOFError, SystemExit):
        break
