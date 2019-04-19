import os
import glob
import shutil
import datetime
import pickle
from flask import Flask, redirect, render_template

from watcher import disable_path, images_path
from cat_alert import CatAlert

app = Flask(__name__)
latest_copied_image = ''

@app.route('/')
def main_page():
    global latest_copied_image
    analyze_result = None
    disable = os.path.exists(disable_path)
    if disable:
        current = "disabled"
        change_to = "enabled"
        change_to_number = 1
    else:
        current = "enabled"
        change_to = "disabled"
        change_to_number = 0
    image_list = glob.glob(images_path + "*.jpg")
    analyzed = [-1, -1, -1]
    if image_list:
        latest_image = max(image_list, key=os.path.getctime)
        if latest_copied_image != latest_image:
            old_images = glob.glob("static/*.jpg")
            for image in old_images:
                os.remove(image)
            shutil.copy(latest_image, "static/")
            latest_copied_image = latest_image
        max_result = -1
        latest_analyzed = latest_image.replace(".jpg", ".anlz")
        if os.path.exists(latest_analyzed):
            analyzed = [round(x, 2) for x in pickle.load(open(latest_analyzed, "rb"))]
    return render_template('main_page.html', change_to_number=change_to_number,
                           change_to=change_to, current=current,
                           image=os.path.basename(latest_copied_image),
                           bawf=analyzed[0], missy=analyzed[2], empty=analyzed[1])

@app.route('/img/<path:filename>') 
def send_file(filename): 
    return send_from_directory('static', filename)
    
@app.route("/<int:change_number>")
def change(change_number):
    if change_number:
        if os.path.exists(disable_path):
            os.remove(disable_path)
    else:
        open(disable_path, "wb")
    return redirect("/")

@app.route("/ksht")
def play_ksht():
    alert = CatAlert(False)
    alert.last_played = datetime.datetime(1970, 1, 1, 2, 0, 0)
    alert.play_ksht()
    return redirect("/")

app.run("0.0.0.0", 1337, threaded=True)
