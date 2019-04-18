import glob
import os
import time
import datetime
import pickle

from watcher import images_path

ksht_delay = 10

class CatAlert:
    def __init__(self, import_analyzer=True):
        self.last_played = datetime.datetime.now()
        self.analyzer = None
        if import_analyzer:
            from analyzer import CatAnalyzer
            self.analyzer = CatAnalyzer()
            self.analyzer.load_model("missy_or_bawf.h5")

    def play_ksht(self):
        now = datetime.datetime.now()
        if (now - self.last_played).seconds > ksht_delay:
            print("playing ksht")
            os.system("ffplay -autoexit -nodisp ksht_aviad.mp3")
            self.last_played = now
        
        
    def run(self):
        if not self.analyzer:
            print("Analyzer not loaded, please create instance again with import_analyzer=True")
            return
        while True:
            print("Checking for bad cats...")
            time.sleep(1)
            image_list = glob.glob(images_path + "*.jpg")
            latest_image = None
            if image_list:
                latest_image = max(image_list, key=os.path.getctime)
            if not latest_image:
                continue
            analyze_file = latest_image.replace(".jpg", ".anlz")
            if os.path.exists(analyze_file):
                continue
            analyze_result = self.analyzer.analyze_picture(latest_image)
            print(analyze_result)
            with open(analyze_file, "wb") as f:
                pickle.dump(analyze_result.tolist(), f)
            if analyze_result[0] > 0.5 and analyze_result[1] < 0.5 and analyze_result[2] < 0.5:
                print("Found a bad cat:", latest_image, "Result", analyze_result)
                self.play_ksht()

if __name__ == '__main__':
    alert = CatAlert()
    alert.run()
