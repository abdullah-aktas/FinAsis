class Gamification:
    """
    Kullanıcıya görevler, ödüller ve rozetler sunan oyunlaştırma modülü.
    """
    def __init__(self):
        self.tasks = ["Giriş Yap", "İlk Eğitimi Tamamla", "Bir Arkadaşını Davet Et"]
        self.rewards = {"Giriş Yap": "Hoşgeldin Rozeti", "İlk Eğitimi Tamamla": "Başlangıç Rozeti", "Bir Arkadaşını Davet Et": "Davet Rozeti"}
        self.completed = []

    def complete_task(self, task):
        if task in self.tasks and task not in self.completed:
            self.completed.append(task)
            return self.rewards.get(task, "Ödül Yok")
        return None 