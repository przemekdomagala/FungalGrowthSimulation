import tkinter as tk
from backend import update_fungal_density_for_one_cell, starting_point_available
import copy
from matplotlib.pylab import randint
import sim_utils as su

from tkinter import PhotoImage

class GridApp:
    def __init__(self, root, rows=40, cols=40, cell_size=15):
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
        self.start_coordinates = tuple()

        self.time_step_hours = 1
        self.diffusion_coefficient = 0.5

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)
        self.grid_frame = tk.Frame(self.main_frame)
        self.grid_frame.pack()

        self.canvas_label = tk.Label(self.grid_frame, text="Kliknij komórkę by ustawić ją jako startową", font="arial 15 bold")
        self.canvas_label.pack()

        self.canvas = tk.Canvas(self.grid_frame, width=cols * cell_size, height=rows * cell_size)
        self.canvas.pack()

        self.image_frame = tk.Frame(self.main_frame)
        self.image_frame.pack(side="left", padx=10, pady=20)

        self.image = PhotoImage(file="image.png")
        self.image_label = tk.Label(self.image_frame, image=self.image)
        self.image_label.pack_forget()
        
        self.buttons_frame = tk.Frame(root)
        self.buttons_frame.pack(pady=10)
        self.start_simulation_button = tk.Button(self.buttons_frame, text="Rozpocznij symulację", font="arial 15 bold", command=self.start_simulation)
        self.randomize_button = tk.Button(self.buttons_frame, text="Losuj wartości parametrów", font="arial 15", command=self.randomize_values)
        self.reset_button = tk.Button(self.buttons_frame, text="Resetuj symulację", font="arial 15 bold", command=self.reset_simulation)
        self.start_simulation_button.pack(side="left", padx=5)
        self.randomize_button.pack(side="left", padx=5)
        self.reset_button.pack(side="left", padx=5)

        self.simulation_started = False

        self.temperature_slider = tk.Scale(root, from_=0, to=30, orient="horizontal", label="Temperatura (°C)")
        self.food_slider = tk.Scale(root, from_=0, to=100, orient="horizontal", label="Poziom pożywienia")
        self.humidity_slider = tk.Scale(root, from_=0, to=100, orient="horizontal", label="Wilgotność (%)")
        self.diffusion_slider = tk.Scale(root, from_=0, to=1, resolution=0.01, orient="horizontal", label="Współczynnik dyfuzji", length=125)
        self.diffusion_slider.set(self.diffusion_coefficient)

        self.mode_buttons_frame = tk.Frame(root)
        self.mode_buttons_frame.pack()

        self.toggle_temp_button = tk.Button(self.mode_buttons_frame, text="Tryb Temperatury", font="arial 15", command=self.toggle_temperature_mode)
        self.toggle_food_button = tk.Button(self.mode_buttons_frame, text="Pożywienie", font="arial 15", command=self.toggle_food_mode)
        self.toggle_humidity_button = tk.Button(self.mode_buttons_frame, text="Tryb Wilgotności", font="arial 15", command=self.toggle_humidity_mode)

        self.toggle_temp_button.pack(side="left", padx=5)
        self.toggle_food_button.pack(side="left", padx=5)
        self.toggle_humidity_button.pack(side="left", padx=5)
        

        self.time_step_label = tk.Label(root, text="Krok czasowy (godziny):", font="arial 12")
        self.time_step_entry = tk.Entry(root, font="arial 12", width=10)
        self.time_step_entry.insert(0, str(self.time_step_hours))
        self.time_step_button = tk.Button(root, text="Ustaw krok", font="arial 12", command=self.set_time_step)
        self.diffusion_slider.pack()
        self.time_step_label.pack()
        self.time_step_entry.pack()
        self.time_step_button.pack()

        self.draw_grid()
        self.canvas.bind("<Button-1>", self.on_click)

    def reset_simulation(self):
        """Resets the simulation to its initial state."""
        
        self.grid_matrix = [[[15, 50, 50, 0] for _ in range(self.cols)] for _ in range(self.rows)]

        self.temperature_slider.set(15)
        self.food_slider.set(50)
        self.humidity_slider.set(50)
        self.diffusion_slider.set(self.diffusion_coefficient)

        self.image_label.pack_forget()

        self.canvas.delete("all")
        self.cells = {}
        self.draw_grid()

        self.simulation_started = False
        self.start_coordinates = tuple()
        if self.current_s_cell:
            self.canvas.delete(self.current_s_cell)
            self.current_s_cell = None

        self.temperature_slider.config(state="normal")
        self.temperature_slider.pack_forget()
        self.food_slider.config(state="normal")
        self.food_slider.pack_forget()
        self.humidity_slider.config(state="normal")
        self.humidity_slider.pack_forget()
        self.diffusion_slider.config(state="normal")
        self.time_step_entry.config(state="normal")
        self.time_step_button.config(state="normal")
        self.toggle_temp_button.config(state="normal")
        self.toggle_temp_button.config(text="Tryb Temperatury")
        self.randomize_button.config(state="normal")
        self.toggle_food_button.config(state="normal")
        self.toggle_food_button.config(text="Pożywienie")
        self.toggle_humidity_button.config(state="normal")
        self.toggle_humidity_button.config(text="Tryb Wilgotności")
        self.start_simulation_button.config(text="Rozpocznij symulację", command=self.start_simulation)
        self.temperature_mode = self.food_mode = self.humidity_mode = False
        self.canvas_label.config(text="Kliknij komórkę by ustawić ją jako startową", fg="black")
        print("Symulacja została zresetowana!")

    def randomize_values(self):
        for i in range(self.rows):
            for j in range(self.cols):
                self.grid_matrix[i][j][0] = randint(0,30)
                self.grid_matrix[i][j][1] = randint(0,100)
                self.grid_matrix[i][j][2] = randint(0,100)
        self.update_cell_colors()

    def start_simulation(self, rows=10, cols=10, cell_size=40):
        """Rozpoczyna symulację i blokuje możliwość zmiany parametrów."""
        if len(self.start_coordinates) == 0:
            self.canvas_label.config(text="Najpierw wybierz komórkę startową!", fg="red")
            return      
        if not starting_point_available(self.grid_matrix, self.start_coordinates[0], self.start_coordinates[1]):
            self.canvas_label.config(text="Wybrana komórka nie spełnia warunków startowych!", fg="red")
            return
        if not self.simulation_started:
            self.canvas_label.config(text="Symulacja rozpoczęta", fg="green")
            self.image_label.pack()
            self.simulation_started = True
            self.grid_frame.pack(side="left", ipadx=10)
            self.start_simulation_button.config(text="Zatrzymaj symulację", command=self.stop_simulation)
            self.temperature_slider.config(state="disabled")
            self.food_slider.config(state="disabled")
            self.humidity_slider.config(state="disabled")
            self.diffusion_slider.config(state="disabled")
            self.time_step_entry.config(state="disabled")
            self.time_step_button.config(state="disabled")
            self.toggle_temp_button.config(state="disabled")
            self.randomize_button.config(state="disabled")
            self.toggle_food_button.config(state="disabled")
            self.toggle_humidity_button.config(state="disabled")
            
            if self.grid_matrix[self.start_coordinates[0]][self.start_coordinates[1]][3] == 0:
                self.grid_matrix[self.start_coordinates[0]][self.start_coordinates[1]][3] = 0.01
            print("Symulacja rozpoczęta! Parametry zostały zablokowane.")
            self.simulate()

    # region simulate
    def simulate(self):
        """Symuluje wzrost grzybni w siatce."""
        if self.simulation_started:
            new_grid = copy.deepcopy(self.grid_matrix)
            for _ in range(int(self.time_step_hours/1)):
                for i in range(self.rows):
                    for j in range(self.cols):
                        new_density = update_fungal_density_for_one_cell(self.grid_matrix, self.diffusion_coefficient, 0.84, 0.1, i, j, self.rows, self.cols)
                        new_grid[i][j][3] = new_density
                        if new_density >= 1:
                            new_grid[i][j][3] = 1.0
                self.grid_matrix = new_grid
            self.update_cell_color()
            self.root.after(1000, self.simulate)


    def update_cell_color(self):
        for rect_id, (row, col) in self.cells.items():
            density = self.grid_matrix[row][col][3]
            color = su.get_cell_color(density)
            self.canvas.itemconfig(rect_id, fill=color)

    def stop_simulation(self):
        """Zatrzymuje symulację i odblokowuje możliwość zmiany parametrów."""
        if self.simulation_started:
            self.simulation_started = False
            self.start_simulation_button.config(text="Wznów symulację", command=self.start_simulation)

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

    def update_diffusion_coefficient(self):
        """Aktualizuje współczynnik dyfuzji na podstawie suwaka."""
        self.diffusion_coefficient = self.diffusion_slider.get()
        print(f"Współczynnik dyfuzji ustawiony na {self.diffusion_coefficient}.")

    def on_click(self, event):
        if(self.simulation_started):
            return
        
        x, y = event.x, event.y
        clicked_cell = self.canvas.find_closest(x, y)
        if clicked_cell:
            cell_id = clicked_cell[0]
            row, col = self.cells[cell_id]

            if self.temperature_mode:
                temperature = self.temperature_slider.get()
                self.grid_matrix[row][col][0] = temperature 
                new_color = su.get_temperature_color(temperature)
                self.canvas.itemconfig(cell_id, fill=new_color)

            elif self.food_mode:
                food_level = self.food_slider.get()
                self.grid_matrix[row][col][1] = food_level
                new_color = su.get_food_color(food_level)
                self.canvas.itemconfig(cell_id, fill=new_color)

            elif self.humidity_mode:
                humidity = self.humidity_slider.get()
                self.grid_matrix[row][col][2] = humidity 
                new_color = su.get_humidity_color(humidity)
                self.canvas.itemconfig(cell_id, fill=new_color)

            else:
                if self.current_s_cell:
                    self.canvas.delete(self.current_s_cell)

                x1, y1 = col * self.cell_size, row * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                text_x = (x1 + x2) / 2
                text_y = (y1 + y2) / 2
                self.current_s_cell = self.canvas.create_text(text_x, text_y, text="S", font=("Arial", 16))
                self.start_coordinates = (row, col)

    def draw_grid(self):
        for row in range(self.rows):
            for col in range(self.cols):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")
                self.cells[rect_id] = (row, col)

    def toggle_temperature_mode(self):
        self.temperature_mode = not self.temperature_mode
        self.food_mode = self.humidity_mode = False
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
        self.temperature_mode = self.humidity_mode = False
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
        self.temperature_mode = self.food_mode = False 
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
                color = su.get_temperature_color(temperature)
            elif self.food_mode:
                food_level = self.grid_matrix[row][col][1]
                color = su.get_food_color(food_level)
            elif self.humidity_mode:
                humidity = self.grid_matrix[row][col][2]
                color = su.get_humidity_color(humidity)
            else:
                color = "white"  
            self.canvas.itemconfig(rect_id, fill=color)


if __name__ == "__main__":
    def center_window(width=300, height=200):
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        x = (screen_width/2) - (width/2)
        y = (screen_height/2) - (height/2)
        root.geometry('%dx%d+%d+%d' % (width, height, x, y-45))
    
    root = tk.Tk()
    frame = tk.Frame(root)
    center_window(800, 990)  
    root.title("Siatka 2D - Skala Temperatury, Pożywienia i Wilgotności")
    app = GridApp(root)
    root.mainloop()
