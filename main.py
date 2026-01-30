import os
import time
import winreg
from datetime import datetime


# Ищем Steam 
def get_steam_path():
    keys = [
        (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam")
    ]
    
    for hkey, path in keys:
        try:
            key = winreg.OpenKey(hkey, path)
            steam_path = winreg.QueryValueEx(key, "SteamPath")[0]
            winreg.CloseKey(key)
            if os.path.exists(steam_path):
                return steam_path
        except:
            continue
    return None


def parse_acf(file_path):
    try:
        data = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if '"' in line:
                    parts = line.strip().replace('"', '').split('\t\t')
                    if len(parts) == 2:
                        data[parts[0].strip()] = parts[1].strip()
        return data
    except:
        return {}


# Получаем название игры
def get_game_name(steam_path, app_id):
    manifest = os.path.join(steam_path, "steamapps", f"appmanifest_{app_id}.acf")
    if os.path.exists(manifest):
        data = parse_acf(manifest)
        return data.get('name', f'AppID_{app_id}')
    return f'AppID_{app_id}'


def get_folder_size(path):
    total = 0
    try:
        for root, dirs, files in os.walk(path):
            for file in files:
                total += os.path.getsize(os.path.join(root, file))
    except:
        pass
    return total


def format_speed(bytes_per_sec):
    units = ['B/s', 'KB/s', 'MB/s', 'GB/s']
    size = bytes_per_sec
    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB/s"


def main():
    print("\n=== Steam Download Monitor ===\n")
    
    steam_path = get_steam_path()
    if not steam_path:
        print("Ошибка: Steam не найден")
        return
    
    print(f"Steam найден: {steam_path}\n")
    
    downloading_path = os.path.join(steam_path, "steamapps", "downloading")
    
    prev_sizes = {}
    
    for i in range(5):
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Проверка #{i+1}")
        print("-" * 50)
        
        if not os.path.exists(downloading_path):
            print("Нет активных загрузок")
        else:
            found = False
            for app_id in os.listdir(downloading_path):
                app_dir = os.path.join(downloading_path, app_id)
                if os.path.isdir(app_dir):
                    found = True
                    
                    game_name = get_game_name(steam_path, app_id)
                    current_size = get_folder_size(app_dir)
                    
                    print(f"\n🎮Игра: {game_name}")
                    
                    # Считаем скорость
                    if app_id in prev_sizes:
                        speed = (current_size - prev_sizes[app_id]) / 60 
                        print(f"🏎️Скорость: {format_speed(speed)}")
                        
                        if speed < 100:
                            print("⏸️Статус: На паузе")
                        else:
                            print("▶️Статус: Загружается")
                    else:
                        print("📊Статус: Первая проверка...")
                    
                    prev_sizes[app_id] = current_size
            
            if not found:
                print("Нет активных загрузок")
        
        if i < 4:
            print("\n⏳Следующая проверка через 60 секунд")
            time.sleep(60)
    
    print("\n\n=== Мониторинг остановлен ===")



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Остановлено")
    except Exception as e:
        print(f"Ошибка: {e}")