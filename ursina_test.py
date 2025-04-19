from ursina import Ursina, Entity, color, Text

app = Ursina()
Entity(model='cube', color=color.orange, scale=(2, 1, 3))
Text(text='Ursina çalışıyor!', origin=(0, 0), scale=2)
app.run() 