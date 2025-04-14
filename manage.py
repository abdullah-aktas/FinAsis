#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy_garden.graph import Graph, MeshLinePlot
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.lang import Builder

# Tema renkleri
COLORS = {
    'primary': '#2196F3',
    'secondary': '#FFC107',
    'success': '#4CAF50',
    'danger': '#F44336',
    'warning': '#FF9800',
    'info': '#00BCD4',
    'light': '#F5F5F5',
    'dark': '#212121',
    'white': '#FFFFFF',
    'black': '#000000',
    'gray': '#9E9E9E'
}

# KV dosyası içeriği
kv_string = '''
#:import get_color_from_hex kivy.utils.get_color_from_hex

<HomeScreen>:
    BoxLayout:
        orientation: 'vertical'
        canvas:
            Color:
                rgba: get_color_from_hex('#F5F5F5')
            Rectangle:
                pos: self.pos
                size: self.size

        BoxLayout:
            size_hint_y: None
            height: '100dp'
            padding: '16dp'
            canvas:
                Color:
                    rgba: get_color_from_hex('#2196F3')
                Rectangle:
                    pos: self.pos
                    size: self.size

            BoxLayout:
                orientation: 'vertical'
                Label:
                    text: 'FinAsis'
                    font_size: '32sp'
                    color: get_color_from_hex('#FFFFFF')
                    bold: True
                Label:
                    text: 'Finansal Yönetim Sistemi'
                    font_size: '16sp'
                    color: get_color_from_hex('#FFFFFF')
                    opacity: 0.8

        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: '16dp'
                spacing: '16dp'

                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: '300dp'
                    padding: '16dp'
                    canvas:
                        Color:
                            rgba: get_color_from_hex('#FFFFFF')
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [8]

                    Label:
                        text: 'Finansal Özet'
                        font_size: '24sp'
                        bold: True
                        size_hint_y: None
                        height: '40dp'

                    Graph:
                        id: graph
                        xlabel: 'Ay'
                        ylabel: 'Değer'
                        x_ticks_minor: 1
                        x_ticks_major: 1
                        y_ticks_major: 20
                        y_grid: True
                        x_grid: True
                        padding: 5
                        x_grid_label: True
                        y_grid_label: True

                GridLayout:
                    cols: 2
                    spacing: '16dp'
                    size_hint_y: None
                    height: self.minimum_height
                    padding: '16dp'

                    Button:
                        text: 'Muhasebe'
                        size_hint_y: None
                        height: '100dp'
                        background_color: get_color_from_hex('#2196F3')
                        on_press: root.show_accounting()

                    Button:
                        text: 'Raporlar'
                        size_hint_y: None
                        height: '100dp'
                        background_color: get_color_from_hex('#2196F3')
                        on_press: root.show_reports()

                    Button:
                        text: 'CRM'
                        size_hint_y: None
                        height: '100dp'
                        background_color: get_color_from_hex('#2196F3')
                        on_press: root.show_crm()

                    Button:
                        text: 'Ayarlar'
                        size_hint_y: None
                        height: '100dp'
                        background_color: get_color_from_hex('#2196F3')
                        on_press: root.show_settings()
'''

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_graph()

    def setup_graph(self):
        graph = self.ids.graph
        plot = MeshLinePlot(color=[1, 1, 1, 1])
        plot.points = [(x, y) for x, y in enumerate([20, 45, 28, 80, 99, 43])]
        graph.add_plot(plot)

    def show_accounting(self):
        print("Muhasebe ekranına geçiş")

    def show_reports(self):
        print("Raporlar ekranına geçiş")

    def show_crm(self):
        print("CRM ekranına geçiş")

    def show_settings(self):
        print("Ayarlar ekranına geçiş")

class FinasisApp(App):
    def build(self):
        # KV dosyasını yükle
        Builder.load_string(kv_string)
        
        # Pencere boyutunu ayarla
        Window.size = (400, 700)
        
        # Ekran yöneticisini oluştur
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        return sm

def run_django():
    """Run Django administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

def run_kivy():
    """Run Kivy mobile application."""
    FinasisApp().run()

def main():
    """Run either Django or Kivy based on command line arguments."""
    if len(sys.argv) > 1 and sys.argv[1] == 'mobile':
        run_kivy()
    else:
        run_django()

if __name__ == '__main__':
    main()
