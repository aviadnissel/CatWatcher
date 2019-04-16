import os
import glob
import shutil
from flask import Flask, redirect, render_template

from catwatcher import disable_path, images_path

app = Flask(__name__)
latest_copied_image = ''

@app.route('/')
def main_page():
    global latest_copied_image
    disable = os.path.exists(disable_path)
    if disable:
        current = "disabled"
        change_to = "enabled"
        change_to_number = 1
    else:
        current = "enabled"
        change_to = "disabled"
        change_to_number = 0
    image_list = glob.glob(images_path + "*orig.jpg")
    if image_list:
        latest_image = max(image_list, key=os.path.getctime)
        if latest_copied_image != latest_image:
            old_images = glob.glob("static/*orig.jpg")
            for image in old_images:
                os.remove(image)
            shutil.copy(latest_image, "static/")
            latest_copied_image = latest_image
    return render_template('main_page.html', change_to_number=change_to_number,
                           change_to=change_to, current=current,
                           image=os.path.basename(latest_copied_image))

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

app.run("0.0.0.0", 1337, threaded=True)
