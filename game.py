import tkinter as tk
from tkinter import messagebox, simpledialog
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import pygame
import threading
from PIL import Image, ImageTk
import os
import time

# Функция для создания отсутствующих файлов
def create_missing_files():
    sound_files = [
        "Connecting to satelite li - Converted Vocals.mp3",
        "Manual mode. Activated. - Converted Vocals.mp3",
        "Automatic control mode on - Converted Vocals.mp3",
        "Nuclear missle. Launch. - Converted Vocals.mp3",
        "Target destroyed. - Converted Vocals.mp3",
        "Forced disconnection from - Converted Vocals.mp3",
        "Colony. Lost - Converted Vocals.mp3",
        "New Tiberium fabrics. Eng - Converted Vocals.mp3",
        "New transportions ships.  - Converted Vocals.mp3",
        "New enemies battleships.  - Converted Vocals.mp3",
        "Mission acomplished. Sign - Converted Vocals.mp3",
        "Commander. You have compl - Converted Vocals.mp3",
        "musi.mp3"
    ]

    image_files = ["AI.jpg", "Kane.jpg"]

    for file in sound_files + image_files:
        if not os.path.exists(file):
            with open(file, 'w') as f:
                pass
            print(f"Создан пустой файл: {file}")


# Инициализация pygame для звуков
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)

# Загрузка звуков (с обработкой ошибок)
def load_sound(filename):
    try:
        return pygame.mixer.Sound(filename)
    except:
        print(f"Ошибка загрузки звука: {filename}")
        return None

sound_create = load_sound('Connecting to satelite li - Converted Vocals.mp3')
sound_manual = load_sound('Manual mode. Activated. - Converted Vocals.mp3')
sound_auto = load_sound('Automatic control mode on - Converted Vocals.mp3')
sound_nuke = load_sound('Nuclear missle. Launch. - Converted Vocals.mp3')
sound_target = load_sound('Target destroyed. - Converted Vocals.mp3')
sound_fatal = load_sound('Forced disconnection from - Converted Vocals.mp3')
sound_colonylost = load_sound('Colony. Lost - Converted Vocals.mp3')
sound_economy = load_sound('New Tiberium fabrics. Eng - Converted Vocals.mp3')
sound_transport = load_sound('New transportions ships.  - Converted Vocals.mp3')
sound_enem = load_sound('New enemies battleships.  - Converted Vocals.mp3')
sound_signal = load_sound('Mission acomplished. Sign - Converted Vocals.mp3')
sound_victory = load_sound('Commander. You have compl - Converted Vocals.mp3')

# Флаг для отслеживания состояния музыки
music_playing = False

# Создаем отсутствующие файлы
create_missing_files()

# Функция для плавного воспроизведения музыки
def play_background_music():
    global music_playing
    try:
        if not music_playing:
            pygame.mixer.music.load('musi.mp3')
            pygame.mixer.music.play(-1)
            music_playing = True
            # Устанавливаем более низкую громкость для фоновой музыки
            pygame.mixer.music.set_volume(0.3)
    except Exception as e:
        print(f"Ошибка загрузки фоновой музыки: {e}")

# Запускаем музыку в отдельном потоке чтобы не блокировать интерфейс
def start_music_thread():
    music_thread = threading.Thread(target=play_background_music, daemon=True)
    music_thread.start()

# Запускаем музыку
start_music_thread()

# Классы для планет и корпораций
class CelestialBody:
    def __init__(self, name):
        self.name = name

class Planet(CelestialBody):
    def __init__(self, name, tiberium_production=50, energy_production=0, technology=1, is_enemy=False):
        super().__init__(name)
        self.tiberium_production = tiberium_production  # базовая выработка тиберия
        self.energy_production = energy_production      # начальная выработка энергии (0)
        self.technology = technology                     # уровень технологий
        self.health = 100                               # здоровье планеты
        self.damage_level = 0                           # степень повреждений
        self.is_enemy = is_enemy                        # враг или союзник
        self.shield_protection_rounds = 0 

class CosmicObject(CelestialBody):
    def __init__(self, number, creation_turn):
        super().__init__(f"cosmic-{number}")  # Имя вида cosmic-1, cosmic-2...
        self.number = number                 # Сохраняем уникальный номер объекта
        self.creation_turn = creation_turn   # Дата появления объекта
        self.researched = False              # Флаг, означающий, что объект пока не изучен                       # был ли объект изучён

class Corporation:
    def __init__(self, name):
        self.name = name

class LogisticsCompany(Corporation):
    def __init__(self, name):
        super().__init__(name)

class TechTrader(Corporation):
    def __init__(self, name):
        super().__init__(name)

class MinerCompany(Corporation):
    def __init__(self, name):
        super().__init__(name)

# Основной класс игры
class GalacticEmpireGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Империя Звёзд")
        self.root.configure(bg='white')
        self.root.geometry("1200x800")
        
        self.graph = nx.Graph()
        self.planets = []       # все планеты (игрока и противника)
        self.your_planets = []  # планеты игрока
        self.enemy_planets = [] # планеты противника
        self.cosmic_objects = [] # космические объекты
        self.corporations = []
        self.current_turn = 0
        self.tiberium = 0          # запас тиберия
        self.energy = 0            # запас энергии
        self.auto_turn_active = False
        self.nuke_cost = 1000      # стоимость ядерной ракеты
        self.planet_destruction_penalty = 2500 # штраф за потерю планеты
        self.upgrade_cost1 = 650   # улучшение производства тиберия
        self.upgrade_cost2 = 350   # улучшение энергетики
        self.victory_threshold = 1000 # условие победы
        self.repair_cost = 300     # стоимость ремонта
        self.research_cost = 2000  # стоимость изучения
        self.shield_cost = 1500    # стоимость силового поля
        self.selected_planet = None
        self.create_ui()
        self.global_shield_counter = 0
        self._total_enemies_count = 2

    def create_ui(self):
        # Основная структура окон
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая панель с кнопками управления
        left_frame = tk.Frame(main_frame, bg='#a6a6a6', width=250, height=420, bd=2, relief='solid')
        left_frame.pack(side=tk.LEFT, anchor='nw', padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # Правая панель с игровым полем
        right_frame = tk.Frame(main_frame, bg='white')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Создание UI элементов слева
        try:
            self.image = Image.open("AI.jpg").resize((80, 60), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(self.image)
            self.image_label = tk.Label(left_frame, image=self.photo, bg='black')
            self.image_label.pack(pady=(0, 10))
        except:
            self.image_label = tk.Label(left_frame, text="AI Image", bg='black', fg='white')
            self.image_label.pack(pady=(0, 10))

        self.text_label = tk.Label(left_frame, text="...To punish and enslave.", bg='#a6a6a6', fg='black')
        self.text_label.pack(pady=(0, 10))

        # Панель кнопок
        button_frame = tk.Frame(left_frame, bg='#404040', width=280) 
        button_frame.pack(fill=tk.X)

        # Кнопки управления
        self.create_button = tk.Button(button_frame, text="Подключиться к сети спутников", 
                                      command=self.create_galaxy, bg='lightgray', fg='black', 
                                      height=2, wraplength=200)
        self.create_button.grid(row=0, column=0, columnspan=2, sticky="ew", padx=2, pady=2)

        self.turn_button = tk.Button(button_frame, text="Следующий Ход", 
                                    command=self.next_turn, bg='lightblue', fg='black',
                                    height=2, wraplength=100)
        self.turn_button.grid(row=1, column=0, sticky="ew", padx=2, pady=2)

        self.auto_turn_button = tk.Button(button_frame, text="Авто контроль", 
                                         command=self.toggle_auto_turn, bg='lightgreen', fg='black',
                                         height=2, wraplength=100)
        self.auto_turn_button.grid(row=1, column=1, sticky="ew", padx=2, pady=2)

        # Магазин и апгрейды
        self.shop_button = tk.Button(button_frame, text="Магазин", 
                                    command=self.open_shop, bg='cyan', fg='black',
                                    height=2, wraplength=100)
        self.shop_button.grid(row=2, column=0, sticky="ew", padx=2, pady=2)

        self.upgrade_button = tk.Button(button_frame, text="Улучшения", 
                                       command=self.open_upgrade_menu, bg='#92d050', fg='black',
                                       height=2, wraplength=100)
        self.upgrade_button.grid(row=2, column=1, sticky="ew", padx=2, pady=2)

        # Ремонтируем планеты
        self.repair_button = tk.Button(button_frame, text="Ремонт", 
                                      command=self.repair_planet_dialog, bg='orange', fg='black',
                                      height=2, wraplength=100)
        self.repair_button.grid(row=3, column=0, sticky="ew", padx=2, pady=2)

        # Исследуем объекты
        self.research_button = tk.Button(button_frame, text="Изучение", 
                                        command=self.research_cosmic_object, bg='#994de5', fg='black',
                                        height=2, wraplength=100)
        self.research_button.grid(row=3, column=1, sticky="ew", padx=2, pady=2)

        for i in range(2):
            button_frame.columnconfigure(i, weight=1)

        # Индикация ресурсов
        self.tiberium_label = tk.Label(left_frame, text="Тиберий: 0", bg='#a6a6a6', fg='black', 
                                    font=("Arial", 12, "bold"))
        self.tiberium_label.pack(pady=(15, 5))

        self.energy_label = tk.Label(left_frame, text="Энергия: 0", bg='#a6a6a6', fg='black', 
                                    font=("Arial", 12, "bold"))
        self.energy_label.pack(pady=5)

        # Создаем игровое поле справа
        self.figure = plt.figure(figsize=(15, 12), facecolor='white')
        self.canvas = FigureCanvasTkAgg(self.figure, master=right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def open_upgrade_menu(self):
        """Меню улучшений."""
        upgrade_window = tk.Toplevel(self.root)
        upgrade_window.title("Улучшения")
        upgrade_window.geometry("400x200")
        upgrade_window.configure(bg='white')

        # Надпись сверху
        title_label = tk.Label(upgrade_window, text="Выберите улучшение:", 
                              bg='white', fg='black', font=("Arial", 14))
        title_label.pack(pady=10)

        # Улучшение добычи тиберия
        tiberium_btn = tk.Button(upgrade_window, text=f"Улучшение заводов тиберия: ({self.upgrade_cost1} тиберия)", 
                                command=lambda: self.upgrade_tiberium(upgrade_window),
                                bg='#70ad47', fg='black', font=("Arial", 12))
        tiberium_btn.pack(pady=10)

        # Улучшение энергетики
        energy_btn = tk.Button(upgrade_window, text=f"Улучшение энергостанций: ({self.upgrade_cost2} тиберия)", 
                              command=lambda: self.upgrade_energy(upgrade_window),
                              bg='#6a8ce0', fg='black', font=("Arial", 12))
        energy_btn.pack(pady=10)

        # Баланс
        balance_label = tk.Label(upgrade_window, text=f"Тиберий: {round(self.tiberium)}", 
                                bg='white', fg='black', font=("Arial", 10))
        balance_label.pack(pady=10)

    def upgrade_tiberium(self, window):
        """Улучшение заводов тиберия."""
        if self.tiberium < self.upgrade_cost1:
            messagebox.showwarning("Ошибка", f"Недостаточно тиберия для улучшения!\nНужно: {self.upgrade_cost1}\nИмеется: {round(self.tiberium)}")
            return

        self.tiberium -= self.upgrade_cost1
        self.tiberium_label.config(text=f"Тиберий: {round(self.tiberium)}")

        # Повышаем добычу тиберия на всех планетах
        for planet in self.your_planets:
            planet.tiberium_production *= 1.2
        
        messagebox.showinfo("Успех", "Количество производимого тиберия за ход увеличилось на 20%!")
        window.destroy()
        self.draw_graph()

    def upgrade_energy(self, window):
        """Улучшение энергостанций."""
        if self.tiberium < self.upgrade_cost2:
            messagebox.showwarning("Ошибка", f"Недостаточно тиберия для улучшения!\nНужно: {self.upgrade_cost2}\nИмеется: {round(self.tiberium)}")
            return

        self.tiberium -= self.upgrade_cost2
        self.tiberium_label.config(text=f"Тиберий: {round(self.tiberium)}")

        # Начальное повышение добычи энергии
        initial_energy_boost = False
        for planet in self.your_planets:
            if planet.energy_production == 0:
                planet.energy_production = 100  # Первоначальный буст
                initial_energy_boost = True
            else:
                planet.energy_production *= 1.2  # Дальнейшее увеличение на 20%
        
        if initial_energy_boost:
            messagebox.showinfo("Успех", "Начато производство энергии! На каждой планете начало производиться 100 единиц энергии за ход!")
        else:
            messagebox.showinfo("Успех", "Количество производимой энергии за ход увеличилось на 20%!")
        window.destroy()
        self.draw_graph()

    def open_shop(self):
        """Магазин доступен только за энергию."""
        shop_window = tk.Toplevel(self.root)
        shop_window.title("Магазин")
        shop_window.geometry("400x200")
        shop_window.configure(bg='white')

        # Надпись сверху
        title_label = tk.Label(shop_window, text="Выберите покупку", bg='white', fg='black', font=("Arial", 14))
        title_label.pack(pady=10)

        # Ядерная ракета
        nuke_btn = tk.Button(shop_window, text=f"Ядерная ракета: ({self.nuke_cost} энергии)", 
                            command=lambda: self.buy_nuke(shop_window),
                            bg='yellow', fg='black', font=("Arial", 12))
        nuke_btn.pack(pady=10)

        # Силовое поле
        shield_btn = tk.Button(shop_window, text=f"Силовое поле: ({self.shield_cost} энергии)", 
                              command=lambda: self.buy_shield(shop_window),
                              bg='cyan', fg='black', font=("Arial", 12))
        shield_btn.pack(pady=10)

        # Баланс
        balance_label = tk.Label(shop_window, text=f"Энергия: {round(self.energy)}", 
                                bg='white', fg='black', font=("Arial", 10))
        balance_label.pack(pady=10)

    def buy_nuke(self, shop_window):
        """Покупка ядерной ракеты доступна за энергию."""
        if self.energy < self.nuke_cost:
            messagebox.showwarning("Ошибка", f"Недостаточно энергии для покупки ракеты!\nНужно: {self.nuke_cost}\nИмеется: {round(self.energy)}")
            return

        self.energy -= self.nuke_cost
        self.energy_label.config(text=f"Энергия: {round(self.energy)}")

        if sound_nuke:
            sound_nuke.play()

        if not self.enemy_planets:
            messagebox.showinfo("Ракета", "Нет целей для атаки!")
            shop_window.destroy()
            return

        target = random.choice(self.enemy_planets)
        if random.random() < 0.75:  # 75% шанс попасть
            self.enemy_planets.remove(target)
            self.planets.remove(target)
            self.graph.remove_node(target.name)
            messagebox.showinfo("Ракета", f"Разрушена планета противника: {target.name}!")
            if sound_target:
                sound_target.play()
        else:
            messagebox.showinfo("Ракета", "Ракета промахнулась!")

        shop_window.destroy()
        self.draw_graph()

    def buy_shield(self, shop_window):
        """Покупка силового поля доступна за энергию."""
        if self.global_shield_counter > 0:
            messagebox.showwarning("Ошибка", "Активно защитное поле!")
            return
    
        if self.energy < self.shield_cost:
            messagebox.showwarning("Ошибка", f"Недостаточно энергии для покупки щита!\nНужно: {self.shield_cost}\nИмеется: {round(self.energy)}")
            return

        self.energy -= self.shield_cost
        self.energy_label.config(text=f"Энергия: {round(self.energy)}")

        # Ставим общий счётчик на 5 защитных циклов
        self.global_shield_counter = 5
    
        messagebox.showinfo("Покупка", f"Силовое поле успешно установлено на все планеты!\nДоступно на {5} ходов.")
        shop_window.destroy()
        self.draw_graph()

    def research_cosmic_object(self):
        """Интерфейс для выбора объекта для изучения."""
        available_objects = [co for co in self.cosmic_objects if not co.researched]
        if not available_objects:
            messagebox.showinfo("Изучение", "Нет доступных объектов для изучения!")
            return

        research_window = tk.Toplevel(self.root)
        research_window.title("Изучение")
        research_window.geometry("400x200")  # Минимальный размер окна
        research_window.minsize(400, 200)    # Окно не может быть меньше этих размеров
        research_window.configure(bg='white')

        # Контейнер для внутренних элементов
        content_frame = tk.Frame(research_window, bg='white')
        content_frame.pack(expand=True, fill=tk.BOTH)

        # Заголовок окна
        title_label = tk.Label(content_frame, text="Выберите объект для изучения:", bg='white', fg='black', font=("Arial", 14))
        title_label.pack(pady=10)

        # Рамка для списка объектов
        list_frame = tk.Frame(content_frame, bg='white')
        list_frame.pack(pady=10)

        # Радио-кнопки для выбора объекта
        selected_object = tk.IntVar(value=0)  # Радиобаттоном выбираем номер объекта

        for idx, cosmic_object in enumerate(available_objects):
            rb = tk.Radiobutton(list_frame, text=f"{cosmic_object.name}",
                                variable=selected_object, value=cosmic_object.number,
                                bg='white', fg='purple', selectcolor='#e6e6e6', font=("Arial", 10))
            rb.pack(anchor='w', padx=20, pady=5)

        # Кнопка для старта исследования
        research_btn = tk.Button(content_frame, text="Изучить выбранный объект",
                                 command=lambda: self.research_selected_object(selected_object.get(), research_window),
                                 bg='purple', fg='black', font=("Arial", 12))
        research_btn.pack(pady=15)

        # Информация о стоимости исследования
        cost_label = tk.Label(content_frame, text=f"Стоимость изучения: {self.research_cost} тиберия",
                              bg='white', fg='black', font=("Arial", 10))
        cost_label.pack(pady=(0, 20))  # Небольшой отступ снизу

        # Динамическая настройка высоты окна
        research_window.update_idletasks()  # Пересчет требований к размеру окна
        current_height = research_window.winfo_reqheight()  # Текущая требуемая высота
        research_window.geometry(f"400x{max(current_height, 200)}")  # Минимум 200 пикселей

    def research_selected_object(self, object_number, window):
        """Изучение"""
        if not object_number:
            messagebox.showwarning("Ошибка", "Выберите объект для изучения!")
            return

        # Поиск объекта по номеру
        cosmic_object = next((co for co in self.cosmic_objects if co.number == int(object_number)), None)
        if not cosmic_object:
            messagebox.showerror("Ошибка", "Объект не найден!")
            return

        if cosmic_object.researched:
            messagebox.showwarning("Ошибка", "Этот объект уже изучен!")
            return

        if self.tiberium < self.research_cost:
            messagebox.showwarning("Ошибка", f"Недостаточно тиберия для изучения!\nНужно: {self.research_cost}\nИмеется: {round(self.tiberium)}")
            return

        # Производим снятие платы и выдачу награды мгновенно
        self.tiberium -= self.research_cost
        reward = random.randint(1000, 10000)
        self.tiberium += reward
        self.tiberium_label.config(text=f"Тиберий: {round(self.tiberium)}")

        # Меняем состояние объекта
        cosmic_object.researched = True

        self.cosmic_objects.remove(cosmic_object)
        self.graph.remove_node(cosmic_object.name)

        # Показываем окно результата изучения
        result_message = f"Объект {cosmic_object.name} изучен.\nПолучено: {reward} тиберия."
        messagebox.showinfo("Изучено", result_message)

        # Закрываем основное окно и обновляем графику
        window.destroy()
        self.draw_graph()

    def check_and_remove_old_cosmic_objects(self):
        """Удаляет устаревшие космические объекты через 20 ходов."""
        expired_objects = [obj for obj in self.cosmic_objects if self.current_turn - obj.creation_turn >= 20]
        for obj in expired_objects:
            self.cosmic_objects.remove(obj)
            self.graph.remove_node(obj.name)
            messagebox.showinfo("Исчезновение объекта", f"Космический объект {obj.name} покинул галактику.")
        self.draw_graph()

    def create_galaxy(self):
        """Создание начальной конфигурации планет."""
        if sound_create:
            sound_create.play()

        # Игровые планеты игрока
        your_planets = [
            Planet("Alpha"), Planet("Beta"), Planet("Gamma"), Planet("Delta"), Planet("Zeta")
        ]

        # Вражеские планеты
        enemy_planets = [
            Planet("Enemy-1", is_enemy=True), Planet("Enemy-2", is_enemy=True)
        ]

        self.planets = your_planets + enemy_planets
        self.your_planets = your_planets
        self.enemy_planets = enemy_planets
        self.cosmic_objects = []
        self.corporations = [
            LogisticsCompany("LogisticsCorp"), TechTrader("TechTraderCorp"), MinerCompany("MinerCorp")
        ]

        # Очистка графа
        self.graph.clear()

        # Добавляем узлы
        for p in self.planets:
            self.graph.add_node(p.name, type="planet", health=p.health, damage_level=p.damage_level, is_enemy=p.is_enemy)

        for co in self.cosmic_objects:
            self.graph.add_node(co.name, type="cosmic_object")

        # Создание связей между планетами
        self.graph.add_edge("Alpha", "Beta", weight=10, safety=0.9)
        self.graph.add_edge("Beta", "Gamma", weight=15, safety=0.8)
        self.graph.add_edge("Gamma", "Alpha", weight=20, safety=0.7)
        self.graph.add_edge("Delta", "Zeta", weight=20, safety=0.8)

        self.draw_graph()

    def draw_graph(self):
        pos = nx.spring_layout(self.graph, k=2, iterations=50)
        plt.clf()

        # Установка белого фона
        self.figure.patch.set_facecolor('white')
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('white')

        # Группировка узлов
        your_planet_nodes = []
        enemy_planet_nodes = []
        cosmic_object_nodes = []

        for node, data in self.graph.nodes(data=True):
            if data.get('type') == 'planet':
                if data.get('is_enemy', False):
                    enemy_planet_nodes.append(node)
                else:
                    your_planet_nodes.append(node)
            elif data.get('type') == 'cosmic_object':
                cosmic_object_nodes.append(node)

        # Цвета для планет игрока в зависимости от состояния
        if your_planet_nodes:
            colors = []
            border_colors = []
            for node in your_planet_nodes:
                health = self.graph.nodes[node].get('health', 100)
                damage_level = self.graph.nodes[node].get('damage_level', 0)

                # Назначаем цвета
                if damage_level == 0:  # Хорошее состояние
                    colors.append('#68f95d')  # Ярко-зеленый
                elif damage_level == 1:  # Средние повреждения
                    colors.append('#119c06')  # Темно-зеленый
                elif damage_level == 2:  # Сильные повреждения
                    colors.append('#084d03')  # Темно-темно-зеленый
                else:  # Полностью разрушенная
                    colors.append('#000000')  # Черный

                # Общую границу устанавливаем зависимо от статуса защиты
                if self.global_shield_counter > 0:
                    border_colors.append('blue')
                else:
                    border_colors.append('black')

            nx.draw_networkx_nodes(self.graph, pos, nodelist=your_planet_nodes, 
                                  node_color=colors, edgecolors=border_colors, 
                                  linewidths=2, node_size=2000, ax=ax)

        # Вражеские планеты красными
        if enemy_planet_nodes:
            nx.draw_networkx_nodes(self.graph, pos, nodelist=enemy_planet_nodes, 
                                  node_color='red', edgecolors='black', 
                                  linewidths=2, node_size=2000, ax=ax)

        # Космические объекты фиолетовыми
        if cosmic_object_nodes:
            nx.draw_networkx_nodes(self.graph, pos, nodelist=cosmic_object_nodes, 
                                  node_color='purple', edgecolors='black', 
                                  linewidths=2, node_size=1800, ax=ax)

        # Невидимые ребра
        nx.draw_networkx_edges(self.graph, pos, ax=ax, alpha=0.0)

        # Подписи узлов
        nx.draw_networkx_labels(self.graph, pos, ax=ax)

        # Без осей
        ax.axis('off')
        self.canvas.draw()

    def repair_planet_dialog(self):
        """Выбор планеты для ремонта."""
        damaged_planets = [p for p in self.your_planets if p.health < 100]
        if not damaged_planets:
            messagebox.showinfo("Ремонт", "Все планеты в отличном состоянии.")
            return

        repair_window = tk.Toplevel(self.root)
        repair_window.title("Ремонт планет")
        repair_window.geometry("400x200")  # Минимальный размер окна
        repair_window.minsize(400, 200)    # Никогда не меньше этих размеров
        repair_window.configure(bg='white')

        # Контейнер для внутреннего содержания
        content_frame = tk.Frame(repair_window, bg='white')
        content_frame.pack(expand=True, fill=tk.BOTH)

        title_label = tk.Label(content_frame, text="Выберите планету для ремонта:", bg='white', fg='black', font=("Arial", 14))
        title_label.pack(pady=10)

        list_frame = tk.Frame(content_frame, bg='white')
        list_frame.pack(pady=10)

        self.selected_planet = tk.StringVar(value="")

        for planet in damaged_planets:
            planet_info = f"{planet.name} - Здоровье: {planet.health}%"
            if planet.health <= 33:
                status = "Большие повреждения"
                color = 'red'
            else:
                status = "Легкие повреждения"
                color = '#eb701d'

            rb = tk.Radiobutton(list_frame, text=f"{planet_info} ({status})", variable=self.selected_planet, value=planet.name, bg='white', fg=color, selectcolor='#e6e6e6', font=("Arial", 10))
            rb.pack(anchor='w', padx=20, pady=5)

        repair_btn = tk.Button(content_frame, text="Отремонтировать", command=lambda: self.repair_selected_planet(repair_window), bg='green', fg='black', font=("Arial", 12))
        repair_btn.pack(pady=15)

        cost_label = tk.Label(content_frame, text=f"Стоимость ремонта: {self.repair_cost} тиберия", bg='white', fg='black', font=("Arial", 10))
        cost_label.pack(pady=(0, 20))  # Верхний отступ 0, нижний — 20 пикселей

        # Динамическое расширение окна
        repair_window.update_idletasks()  # Обновляем содержимое окна
        current_height = repair_window.winfo_reqheight()  # Высоту считаем автоматически
        repair_window.geometry(f"400x{max(current_height, 200)}")  # Высота минимум 200 пикселей

    def repair_selected_planet(self, window):
        """Ремонт конкретной планеты."""
        if not self.selected_planet.get():
            messagebox.showwarning("Ошибка", "Выберите планету для ремонта!")
            return

        planet_name = self.selected_planet.get()
        planet = next((p for p in self.your_planets if p.name == planet_name), None)

        if not planet:
            messagebox.showerror("Ошибка", "Планета не найдена!")
            return

        if self.tiberium < self.repair_cost:
            messagebox.showwarning("Ошибка", f"Недостаточно тиберия для ремонта!\nНеобходимо: {self.repair_cost}\nИмеется: {self.tiberium}")
            return

        planet.health = 100
        planet.damage_level = 0
        self.tiberium -= self.repair_cost
        self.tiberium_label.config(text=f"Тиберий: {round(self.tiberium)}")

        self.graph.nodes[planet.name]['health'] = planet.health
        self.graph.nodes[planet.name]['damage_level'] = planet.damage_level

        window.destroy()
        messagebox.showinfo("Ремонт завершен", f"Планета {planet.name} полностью отремонтирована.")
        self.draw_graph()

    def next_turn(self):
        """Ход игры."""
        self.current_turn += 1

        # Удаляем старые космические объекты
        self.check_and_remove_old_cosmic_objects()

        # Зарабатываем ресурсы
        self.collect_resources()

        # Нападения врагов
        self.handle_enemy_attacks()

        # Периодически создаём новые космические объекты
        if self.current_turn % 8 == 0:
            self.add_cosmic_object()

        # Периодически добавляем новых врагов
        if self.current_turn % 5 == 0:
            self.add_enemy_planets(2)

        self.draw_graph()

        # Победа достигается, когда собрано нужное количество тиберия
        if self.tiberium >= self.victory_threshold:
            self.end_game_victory("Победа достигнута!")

    def check_and_remove_old_cosmic_objects(self):
        """Удаляет устаревшие космические объекты через 20 ходов."""
        old_objects = [obj for obj in self.cosmic_objects if self.current_turn - obj.creation_turn >= 20]
        for obj in old_objects:
            self.cosmic_objects.remove(obj)
            self.graph.remove_node(obj.name)
            messagebox.showinfo("Исчезновение объекта", f"Космический объект {obj.name} покинул галактику.")
        self.draw_graph()

    def handle_enemy_attacks(self):
        """Обработка атак врагов."""
        if not self.enemy_planets or not self.your_planets:
            return

        # Определяем частоту атак
        num_enemies = len(self.enemy_planets)
        base_attack_chance = 0.1 + num_enemies * 0.1
        attack_chance = min(1.0, base_attack_chance)  # Максимум 100%

        # Количество атак за ход
        attacks_per_turn = 1
        if num_enemies >= 5:
            attacks_per_turn = 2
        if num_enemies >= 10:
            attacks_per_turn = 4

        # Выполняем атаки
        for _ in range(attacks_per_turn):
            if random.random() < attack_chance:
                attacker = random.choice(self.enemy_planets)
                target = random.choice(self.your_planets)

                # Проверка защиты (если активировано силовое поле)
                if self.global_shield_counter > 0:
                    self.global_shield_counter -= 1
                    messagebox.showinfo("Щит сработал", f"Противник {attacker.name} попытался атаковать планету {target.name}, но столкнулся с защитой!")
                    continue

                # Определим наносимый урон
                if target.damage_level == 0:
                    damage = 34  # оставляем 66% здоровья
                    damage_type = "поврежден"
                elif target.damage_level == 1:
                    damage = 33  # оставляем 33% здоровья
                    damage_type = "сильно поврежден"
                else:
                    damage = 100  # полное уничтожение
                    damage_type = "уничтожен"

                # Применяем урон
                target.health = max(0, target.health - damage)
                if target.health <= 0:
                    target.damage_level = 3
                elif target.health <= 33:
                    target.damage_level = 2
                elif target.health <= 66:
                    target.damage_level = 1
                else:
                    target.damage_level = 0

                # Обновляем узел в графе
                self.graph.nodes[target.name]['health'] = target.health
                self.graph.nodes[target.name]['damage_level'] = target.damage_level

                # Выведем сообщение о результатах атаки
                if target.health <= 0:
        
                    self.your_planets.remove(target)
                    self.planets.remove(target)
                    self.graph.remove_node(target.name)
                    self.tiberium -= self.planet_destruction_penalty
                    if self.tiberium < 0:
                        self.tiberium = 0
                    self.tiberium_label.config(text=f"Тиберий: {round(self.tiberium)}")
                    messagebox.showinfo("Уничтожение", f"Противник {attacker.name} уничтожил планету {target.name}!")

                    # Если все планеты уничтожены, вызываем конец игры
                    if not self.your_planets:
                        self.end_game_defeat("Игра проиграна. Все колонии уничтожены.")

                else:
                    messagebox.showinfo("Повреждение", f"Противник {attacker.name} повредил планету {target.name}!\nТип ущерба: {damage_type}.\nЗдоровье: {target.health}%.")

        # Перерисовываем карту
        self.draw_graph()

    def add_cosmic_object(self):
        """Добавляет новый космический объект каждые 8 ходов."""
        # Внутренний счетчик общих космических объектов
        self._total_cosmic_objects_count = getattr(self, '_total_cosmic_objects_count', 0)
        new_number = self._total_cosmic_objects_count + 1  # Новое уникальное имя
        new_object = CosmicObject(new_number, self.current_turn)
        self.cosmic_objects.append(new_object)
        self.graph.add_node(new_object.name, type="cosmic_object")
        self._total_cosmic_objects_count += 1  # Увеличили счетчик
        messagebox.showinfo("Космический объект", f"Появился новый объект: {new_object.name}.")
        self.draw_graph()

    def add_enemy_planets(self, count):
        """Добавляет новые вражеские планеты каждые 5 ходов."""
        # Внутренний счетчик появится отдельно и не зависит от длины существующего списка
        self._total_enemies_count = getattr(self, '_total_enemies_count', 0)  # Глобальный счетчик всех врагов
        start_index = self._total_enemies_count + 1  # Индекс первой новой планеты
        for _ in range(count):
            new_enemy = Planet(f"Enemy-{start_index}", is_enemy=True)
            self.enemy_planets.append(new_enemy)
            self.planets.append(new_enemy)
            self.graph.add_node(new_enemy.name, type="planet", health=100, damage_level=0, is_enemy=True)
            start_index += 1  # Следующая планета получит увеличенное значение
        self._total_enemies_count += count  # Обновляем счетчик общей численности врагов
        messagebox.showinfo("Враг", f"Прилетели новые враги: {count} планет.")
        self.draw_graph()

    def collect_resources(self):
        """Собираем ресурсы с наших планет."""
        total_tiberium = sum(planet.tiberium_production for planet in self.your_planets)
        total_energy = sum(planet.energy_production for planet in self.your_planets)
        self.tiberium += total_tiberium
        self.energy += total_energy
        self.tiberium_label.config(text=f"Тиберий: {round(self.tiberium)}")
        self.energy_label.config(text=f"Энергия: {round(self.energy)}")

    def toggle_auto_turn(self):
        """Включает автоматический режим ходов."""
        if self.auto_turn_active:
            self.auto_turn_active = False
            self.auto_turn_button.config(text="Авто контроль")
            if sound_manual:
                sound_manual.play()
        else:
            self.auto_turn_active = True
            self.auto_turn_button.config(text="Остановить авто")
            if sound_auto:
                sound_auto.play()
            self.start_auto_turn()

    def start_auto_turn(self):
        """Автоматически повторяет ход каждые три секунды."""
        if self.auto_turn_active:
            self.next_turn()
            self.root.after(3000, self.start_auto_turn)

    def end_game_victory(self, message):
        messagebox.showinfo("Конец игры", message)
        if "Победа" in message:
            self.show_victory_menu()  # Должен вызывать show_victory_menu
        else:
            if sound_fatal:
                sound_fatal.play()

    def end_game_defeat(self, message):
        """
        Завершает игру с соответствующим сообщением и закрывает окно.
        """
        # Создаем топ-уровневое окно для отображения результата
        final_window = tk.Toplevel(self.root)
        final_window.title("Конец игры")
        final_window.geometry("400x150")
        final_window.configure(bg='white')
    
        # Настраиваем обработчик закрытия окна (крестик)
        final_window.protocol("WM_DELETE_WINDOW", lambda: [final_window.destroy(), self.root.quit()])

        # Добавляем текст в окно
        label = tk.Label(final_window, text=message, 
                        bg='white', fg='black', font=("Arial", 14))
        label.pack(pady=20)

        # Кнопка выхода из игры
        exit_btn = tk.Button(final_window, text="Выйти из игры", 
                            command=lambda: [final_window.destroy(), self.root.quit()],
                            bg='#ff6b6b', fg='black', font=("Arial", 12))
        exit_btn.pack(pady=10)

        # Фоновый звук поражения
        if sound_fatal:
            sound_fatal.play()

        # Центрируем окно
        final_window.transient(self.root)
        final_window.grab_set()
        self.root.wait_window(final_window)      

    def show_victory_menu(self):
        sound_victory.play()
        victory_window = tk.Toplevel(self.root)
        victory_window.title("Победа!")
        victory_window.configure(bg='black')
    
        # Настраиваем обработчик закрытия окна (крестик) - закрывает всю игру
        victory_window.protocol("WM_DELETE_WINDOW", lambda: [victory_window.destroy(), self.root.quit()])
    
        # Центрируем окно относительно главного окна
        victory_window.transient(self.root)
        victory_window.grab_set()
    
        # Центрирование на экране
        victory_window.update_idletasks()
        x = (victory_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (victory_window.winfo_screenheight() // 2) - (500 // 2)
        victory_window.geometry(f"750x300+{x}+{y}")

        # Фрейм для центрирования содержимого
        center_frame = tk.Frame(victory_window, bg='black')
        center_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        # Загрузка изображения
        try:
            victory_image = Image.open("Kane.jpg")
            victory_photo = ImageTk.PhotoImage(victory_image)
    
            # Создание метки для изображения
            victory_image_label = tk.Label(center_frame, image=victory_photo, bg='black')
            victory_image_label.image = victory_photo  # Сохранение ссылки на изображение
            victory_image_label.pack(pady=(0, 20))
        except:
            # Если изображение не загрузилось
            victory_text_label = tk.Label(center_frame, text="ПОБЕДА!", 
                                       bg='black', fg='gold', font=("Helvetica", 24, "bold"))
            victory_text_label.pack(pady=(0, 20))

        # Текст победы по центру
        victory_texts = [
            "Commander. You have completed the task assigned to you,",
            "you have ensured the development of the economy on the colonies allocated to you.",
            "Troops of the NOD brotherhood have been sent to this region,",
            "so you can proceed to the next tasks. Thank you for your service to the brotherhood."
        ]

        for text in victory_texts:
            victory_text_label = tk.Label(center_frame, text=text, 
                                        bg='black', fg='red', font=("Helvetica", 12),
                                        justify=tk.CENTER)
            victory_text_label.pack(pady=2)

        # Функция для проверки звука и выхода
        def check_sound_and_exit():
            while pygame.mixer.get_busy():
                victory_window.update()
                time.sleep(0.1)
            victory_window.destroy()
            self.root.quit()

        # Запускаем проверку в отдельном потоке
        threading.Thread(target=check_sound_and_exit, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    game = GalacticEmpireGame(root)
    root.mainloop()
