import pygal
from datetime import datetime
import os


def create_picture(items, field):
    print("Creating chart...")
    try:
        chart = pygal.Line()
        times = map(datetime.fromtimestamp, [item['time'] for item in items])
        times = map(lambda d: d.strftime('%H:%M:%S'), times)
        chart.x_labels = list(map(str, times))

        values = list(map(lambda x: int(x[0]), [item[field] for item in items]))
        chart.add(field, values)

        chart.render_to_file("./test.svg")
        chart.render_to_png("./test.png")
    except Exception as e:
        print(e)


def clear_folder(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)
