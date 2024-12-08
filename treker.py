import gpxpy
import math
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import time
# Функция для выбора файла GPX
def select_gpx_file():
    root = tk.Tk()
    root.withdraw()  # Скрываем главное окно
    file_path = filedialog.askopenfilename(filetypes=[("GPX files", "*.gpx")])
    return file_path
# Функция для вычисления расстояния (формула Гаверсинуса)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Радиус Земли в км
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    # Вычисляем расстояние
    P = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    Q = 2 * math.asin(math.sqrt(P))
    horizontal_distance = R * Q  # Расстояние в км
    return horizontal_distance
# Выбор файла GPX
gpx_file_path = select_gpx_file()
print(f"Имя обрабатываемого файла: {gpx_file_path}")
# Чтение GPX файла
with open(gpx_file_path, 'r') as gpx_file:
    gpx = gpxpy.parse(gpx_file)
# Получение названия трека
track_name = gpx.tracks[0].name if gpx.tracks else 'Нет названия трека'
# Получение путевых отметок (если имеются)
waypoints = gpx.waypoints
# Вывод путевых отметок
if waypoints:
    print("Путевые отметки:")
    for wpt in waypoints:
        print(
            f'  Название: {wpt.name}, Координаты: {wpt.latitude}, {wpt.longitude}, Высота: {wpt.elevation if wpt.elevation is not None else "Не указана"} м')
else:
    print("Путевых отметок нет")
# Получение всех точек в сегментах
points = []
if gpx.tracks and gpx.tracks[0].segments:
    for segment in gpx.tracks[0].segments:
        points.extend(segment.points)
# Вычисление общей длины маршрута
route_length_km = 0.0
total_ascent_m = 0.0
total_descent_m = 0.0
total_time_seconds = 0.0
previous_time = None
if len(points) > 0:
    start_point = points[0]
    end_point = points[-1]
    for i in range(len(points) - 1):
        # Вычисление расстояния
        route_length_km += haversine(points[i].latitude, points[i].longitude,
                                     points[i + 1].latitude, points[i + 1].longitude)
        # Перепады высот
        alt1 = points[i].elevation if points[i].elevation is not None else 0
        alt2 = points[i + 1].elevation if points[i + 1].elevation is not None else 0
        vertical_change = alt2 - alt1
        if vertical_change > 0:
            total_ascent_m += vertical_change
        else:
            total_descent_m += abs(vertical_change)
        # Нахождение временных меток
        if points[i].time:
            if previous_time:
                delta_time = (points[i].time - previous_time).total_seconds()
                total_time_seconds += delta_time  # Суммируем время
            previous_time = points[i].time
        elif points[i].time_str:
            formatted_time = time.strptime(points[i].time_str)
            current_time = datetime.fromtimestamp(time.mktime(formatted_time))
            if previous_time:
                delta_time = (current_time - previous_time).total_seconds()
                total_time_seconds += delta_time
            previous_time = current_time
    # Подсчет скоростей
    if total_time_seconds > 0:
        average_speed_kmh = (route_length_km / (total_time_seconds / 3600)) if total_time_seconds else 0
        min_speed_kmh = average_speed_kmh
        max_speed_kmh = average_speed_kmh
    else:
        average_speed_kmh = min_speed_kmh = max_speed_kmh = 0
    # Вывод результатов
    print(f'\nНазвание трека: {track_name}')
    print(
        f'Начальная точка: ({start_point.latitude}, {start_point.longitude}), Высота: {start_point.elevation if start_point.elevation is not None else "Не указана"} м')
    print(
        f'Конечная точка: ({end_point.latitude}, {end_point.longitude}), Высота: {end_point.elevation if end_point.elevation is not None else "Не указана"} м')
    print(f'Длина маршрута: {route_length_km:.2f} км')
    print(f'Суммарный подъем: {total_ascent_m / 1000:.2f} км')
    print(f'Суммарный спуск: {total_descent_m / 1000:.2f} км')
    print(f'Общий перепад высот: {(total_ascent_m + total_descent_m) / 1000:.2f} км')
    if previous_time is not None:
        print(
            f'Общее время: {total_time_seconds // 3600} ч {((total_time_seconds % 3600) // 60)} мин {total_time_seconds % 60} сек')
        print(f'Средняя скорость: {average_speed_kmh:.2f} км/ч')
        print(f'Минимальная скорость: {min_speed_kmh:.2f} км/ч')
        print(f'Максимальная скорость: {max_speed_kmh:.2f} км/ч')
    else:
        print('Временных точек нет')
else:
    print('Не удалось найти точки в треке.')