def get_temperature_color(temperature):
    if temperature <= 15:
        ratio = temperature / 15
        red = int(ratio * 255)
        green = 255
        blue = int((1 - ratio) * 255)
    else:
        ratio = (temperature - 15) / 15
        red = 255
        green = int((1 - ratio) * 255)
        blue = 0
    return f"#{red:02x}{green:02x}{blue:02x}"

def get_food_color(food_level):
    start_color = (255, 240, 225)  
    end_color = (128, 0, 0)       
    red = int(start_color[0] + (end_color[0] - start_color[0]) * (food_level / 100))
    green = int(start_color[1] + (end_color[1] - start_color[1]) * (food_level / 100))
    blue = int(start_color[2] + (end_color[2] - start_color[2]) * (food_level / 100))
    return f"#{red:02x}{green:02x}{blue:02x}"

def get_humidity_color(humidity):
    start_color = (255, 228, 200)  
    end_color = (48, 25, 52)   
    red = int(start_color[0] + (end_color[0] - start_color[0]) * (humidity / 100))
    green = int(start_color[1] + (end_color[1] - start_color[1]) * (humidity / 100))
    blue = int(start_color[2] + (end_color[2] - start_color[2]) * (humidity / 100))
    return f"#{red:02x}{green:02x}{blue:02x}"

def get_cell_color(density):

        gradient_colors = [
            (128, 0, 128),   
            (0, 128, 255),  
            (0, 255, 128),  
            (255, 255, 0) 
        ]

        gradient_positions = [0.0, 0.33, 0.66, 1.0]

        for i in range(len(gradient_positions) - 1):
            if gradient_positions[i] <= density <= gradient_positions[i + 1]:
                start_color = gradient_colors[i]
                end_color = gradient_colors[i + 1]
                start_pos = gradient_positions[i]
                end_pos = gradient_positions[i + 1]
                t = (density - start_pos) / (end_pos - start_pos)
                red = int(start_color[0] + (end_color[0] - start_color[0]) * t)
                green = int(start_color[1] + (end_color[1] - start_color[1]) * t)
                blue = int(start_color[2] + (end_color[2] - start_color[2]) * t)
                return f"#{red:02x}{green:02x}{blue:02x}"

        return "#000000"