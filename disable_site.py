import os
from flask import Flask, redirect

disable_path = "/home/pi/disable_watch"
link_template = "<a href=/{change_number}>{change_to}</a>"
app = Flask(__name__)

@app.route('/')
def main_page():
    disable = os.path.exists(disable_path)
    if disable:
        return link_template.format(change_number=1, change_to="enable")
    return link_template.format(change_number=0, change_to="disable")
    
@app.route("/<int:change_number>")
def change(change_number):
    if change_number:
        if os.path.exists(disable_path):
            os.remove(disable_path)
    else:
        open(disable_path, "wb")
    return redirect("/")

app.run("0.0.0.0", 1337)
