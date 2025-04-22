from ursina import color

# Eksik renkleri tanımla
if not hasattr(color, 'light_blue'):
    color.light_blue = color.rgb(100, 149, 237)  # Cornflower blue

if not hasattr(color, 'dark_green'):
    color.dark_green = color.rgb(0, 100, 0)

if not hasattr(color, 'light_gray'):
    color.light_gray = color.rgb(211, 211, 211)

# Renk yardımcıları
def get_color_by_name(name):
    """İsimle renk döndür, eğer renk yoksa benzer bir renk öner"""
    if hasattr(color, name):
        return getattr(color, name)
    
    # Benzer renkleri öner
    color_map = {
        'light_blue': color.light_blue,
        'lightblue': color.light_blue,
        'dark_green': color.dark_green,
        'darkgreen': color.dark_green,
        'light_gray': color.light_gray,
        'lightgray': color.light_gray,
    }
    
    return color_map.get(name, color.white)

# Finansal durum renkleri
def get_financial_status_color(value, threshold_good=0, threshold_danger=-1000):
    """Finansal değere göre renk döndür (pozitif=yeşil, negatif=kırmızı)"""
    if value >= threshold_good:
        return color.green
    elif value <= threshold_danger:
        return color.red
    else:
        # Değere göre sarı-kırmızı arası bir renk
        t = (value - threshold_danger) / (threshold_good - threshold_danger)
        return color.lerp(color.red, color.yellow, t)

# Yaş grubuna göre renk şeması
def get_age_group_colors(age_group):
    """Yaş grubuna göre renk şeması döndür"""
    if age_group == 'child':  # 5-12
        return {
            'primary': color.light_blue,
            'secondary': color.yellow,
            'accent': color.green,
            'text': color.black,
            'background': color.white
        }
    elif age_group == 'teen':  # 13-18
        return {
            'primary': color.blue,
            'secondary': color.orange,
            'accent': color.purple,
            'text': color.black,
            'background': color.white
        }
    elif age_group == 'adult':  # 19-65
        return {
            'primary': color.azure,
            'secondary': color.orange,
            'accent': color.red,
            'text': color.black,
            'background': color.light_gray
        }
    elif age_group == 'senior':  # 65+
        return {
            'primary': color.dark_green,
            'secondary': color.brown,
            'accent': color.gold,
            'text': color.white,
            'background': color.dark_gray
        }
    else:
        # Varsayılan
        return {
            'primary': color.blue,
            'secondary': color.orange,
            'accent': color.green,
            'text': color.black,
            'background': color.white
        } 