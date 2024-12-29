import tkinter as tk
from backend import update_fungal_density_for_one_cell

class GridApp:
    def __init__(self, root, rows=10, cols=10, cell_size=40):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.cells = {}
        self.grid_matrix = [[[15, 50, 50, 0] for _ in range(cols)] for _ in range(rows)]
        self.temperature_mode = False
        self.food_mode = False
        self.humidity_mode = False
        self.current_s_cell = None
        self.time_step_hours = 1  # Domyślny krok czasowy w godzinach


        self.canvas_label = tk.Label(root, text="Kliknij komórkę by ustawić ją jako startową", font="arial 15 bold")
        self.canvas = tk.Canvas(root, width=cols * cell_size, height=rows * cell_size)
        self.canvas_label.pack()
        self.canvas.pack()

        # Suwaki i przyciski trybów
        self.temperature_slider = tk.Scale(root, from_=0, to=30, orient="horizontal", label="Temperatura (°C)")
        self.food_slider = tk.Scale(root, from_=0, to=100, orient="horizontal", label="Poziom pożywienia")
        self.humidity_slider = tk.Scale(root, from_=0, to=100, orient="horizontal", label="Wilgotność (%)")

        self.toggle_temp_button = tk.Button(root, text="Tryb Temperatury", font="arial 15", command=self.toggle_temperature_mode)
        self.toggle_food_button = tk.Button(root, text="Tryb Pożywienia", font="arial 15", command=self.toggle_food_mode)
        self.toggle_humidity_button = tk.Button(root, text="Tryb Wilgotności", font="arial 15", command=self.toggle_humidity_mode)

        # Pole wejściowe kroku czasowego
        self.time_step_label = tk.Label(root, text="Krok czasowy (godziny):", font="arial 12")
        self.time_step_entry = tk.Entry(root, font="arial 12", width=10)
        self.time_step_entry.insert(0, str(self.time_step_hours))  # Ustaw domyślną wartość
        self.time_step_button = tk.Button(root, text="Ustaw krok", font="arial 12", command=self.set_time_step)

        # Umieszczanie elementów GUI
        self.toggle_temp_button.pack()
        self.toggle_food_button.pack()
        self.toggle_humidity_button.pack()
        self.time_step_label.pack()
        self.time_step_entry.pack()
        self.time_step_button.pack()

        self.draw_grid()
        self.canvas.bind("<Button-1>", self.on_click)

    def set_time_step(self):
        """Ustawia krok czasowy na podstawie wartości w polu tekstowym."""
        try:
            new_step = int(self.time_step_entry.get())
            if new_step > 0:
                self.time_step_hours = new_step
                print(f"Krok czasowy ustawiony na {self.time_step_hours} godzin.")
            else:
                print("Wartość kroku czasowego musi być większa niż 0.")
        except ValueError:
            print("Wprowadź poprawną liczbę całkowitą dla kroku czasowego.")

    # Reszta metod pozostaje bez zmian.


    def on_click(self, event):
        x, y = event.x, event.y

        # Znajdź ID klikniętej kratki
        clicked_cell = self.canvas.find_closest(x, y)
        if clicked_cell:
            cell_id = clicked_cell[0]
            row, col = self.cells[cell_id]

            if self.temperature_mode:
                temperature = self.temperature_slider.get()
                self.grid_matrix[row][col][0] = temperature  # Aktualizuj temperaturę w macierzy
                new_color = self.get_temperature_color(temperature)
                self.canvas.itemconfig(cell_id, fill=new_color)

            elif self.food_mode:
                food_level = self.food_slider.get()
                self.grid_matrix[row][col][1] = food_level  # Aktualizuj poziom pożywienia w macierzy
                new_color = self.get_food_color(food_level)
                self.canvas.itemconfig(cell_id, fill=new_color)

            elif self.humidity_mode:
                humidity = self.humidity_slider.get()
                self.grid_matrix[row][col][2] = humidity  # Aktualizuj wilgotność w macierzy
                new_color = self.get_humidity_color(humidity)
                self.canvas.itemconfig(cell_id, fill=new_color)

            else:
                # Usuń poprzednią literkę "S", jeśli istnieje
                if self.current_s_cell:
                    self.canvas.delete(self.current_s_cell)

                # Dodaj literkę "S" w środku klikniętej komórki
                x1, y1 = col * self.cell_size, row * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                text_x = (x1 + x2) / 2
                text_y = (y1 + y2) / 2
                self.current_s_cell = self.canvas.create_text(text_x, text_y, text="S", font=("Arial", 16))



    def draw_grid(self):
        for row in range(self.rows):
            for col in range(self.cols):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                # Narysuj prostokąt z domyślnym kolorem (białym)
                rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")
                self.cells[rect_id] = (row, col)  # Mapowanie ID na współrzędne w macierzy

    


    def toggle_temperature_mode(self):
        self.temperature_mode = not self.temperature_mode
        self.food_mode = self.humidity_mode = False  # Wyłącz inne tryby
        self.update_buttons()
        if self.temperature_mode:
            self.temperature_slider.pack()
            self.temperature_slider.set(15)
            self.food_slider.pack_forget()
            self.humidity_slider.pack_forget()
        else:
            self.temperature_slider.pack_forget()
        self.update_cell_colors()

    def toggle_food_mode(self):
        self.food_mode = not self.food_mode
        self.temperature_mode = self.humidity_mode = False  # Wyłącz inne tryby
        self.update_buttons()
        if self.food_mode:
            self.food_slider.pack()
            self.food_slider.set(50)
            self.temperature_slider.pack_forget()
            self.humidity_slider.pack_forget()
        else:
            self.food_slider.pack_forget()
        self.update_cell_colors()

    def toggle_humidity_mode(self):
        self.humidity_mode = not self.humidity_mode
        self.temperature_mode = self.food_mode = False  # Wyłącz inne tryby
        self.update_buttons()
        if self.humidity_mode:
            self.humidity_slider.pack()
            self.humidity_slider.set(50)
            self.temperature_slider.pack_forget()
            self.food_slider.pack_forget()
        else:
            self.humidity_slider.pack_forget()
        self.update_cell_colors()

    def update_buttons(self):
        self.toggle_temp_button.config(text="Tryb Temperatury" if not self.temperature_mode else "Tryb ON")
        self.toggle_food_button.config(text="Tryb Pożywienia" if not self.food_mode else "Tryb ON")
        self.toggle_humidity_button.config(text="Tryb Wilgotności" if not self.humidity_mode else "Tryb ON")

    def update_cell_colors(self):
        for rect_id, (row, col) in self.cells.items():
            if self.temperature_mode:
                temperature = self.grid_matrix[row][col][0]
                color = self.get_temperature_color(temperature)
            elif self.food_mode:
                food_level = self.grid_matrix[row][col][1]
                color = self.get_food_color(food_level)
            elif self.humidity_mode:
                humidity = self.grid_matrix[row][col][2]
                color = self.get_humidity_color(humidity)
            else:
                color = "white"  # Domyślny kolor
            self.canvas.itemconfig(rect_id, fill=color)

    def get_temperature_color(self, temperature):
        # Skala temperatury od 0 (niebieski) do 30 (czerwony) z przejściem przez zielony
        if temperature <= 15:
            # Przejście od niebieskiego do zielonego (0-15)
            ratio = temperature / 15
            red = int(ratio * 255)
            green = 255
            blue = int((1 - ratio) * 255)
        else:
            # Przejście od zielonego do czerwonego (15-30)
            ratio = (temperature - 15) / 15
            red = 255
            green = int((1 - ratio) * 255)
            blue = 0
        return f"#{red:02x}{green:02x}{blue:02x}"

    def get_food_color(self, food_level):
        # Skala pożywienia od 0 (jasny beż) do 100 (ciemny czerwony)

        # Kolory krańcowe gradientu
        start_color = (255, 240, 225)  # Jasny beż
        end_color = (128, 0, 0)        # Ciemny czerwony

        # Interpolacja kolorów
        red = int(start_color[0] + (end_color[0] - start_color[0]) * (food_level / 100))
        green = int(start_color[1] + (end_color[1] - start_color[1]) * (food_level / 100))
        blue = int(start_color[2] + (end_color[2] - start_color[2]) * (food_level / 100))

        return f"#{red:02x}{green:02x}{blue:02x}"

    def get_humidity_color(self, humidity):
        # Skala wilgotności od 0 (jasny beż) do 100 (ciemny fiolet)

        # Kolory krańcowe gradientu
        start_color = (255, 228, 200)  # Jasny beż
        end_color = (48, 25, 52)       # Ciemny fiolet

        # Interpolacja kolorów
        red = int(start_color[0] + (end_color[0] - start_color[0]) * (humidity / 100))
        green = int(start_color[1] + (end_color[1] - start_color[1]) * (humidity / 100))
        blue = int(start_color[2] + (end_color[2] - start_color[2]) * (humidity / 100))

        return f"#{red:02x}{green:02x}{blue:02x}"


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Siatka 2D - Skala Temperatury, Pożywienia i Wilgotności")
    app = GridApp(root)
    root.mainloop()
