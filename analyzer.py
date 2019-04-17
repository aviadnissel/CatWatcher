import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator 
from keras.models import Sequential 
from keras.layers import Conv2D, MaxPooling2D 
from keras.layers import Activation, Dropout, Flatten, Dense 
from keras import backend as K 
import numpy as np
from keras.preprocessing import image
import sys

class CatAnalyzer():
    def __init__(self):
        img_width = 500
        img_height = 375

        if K.image_data_format() == 'channels_first': 
            self.input_shape = (3, img_width, img_height) 
        else: 
            self.input_shape = (img_width, img_height, 3)
        self.model = None

    def load_model(self, model_file):

        model = Sequential() 
        model.add(Conv2D(32, (2, 2), input_shape=self.input_shape)) 
        model.add(Activation('relu')) 
        model.add(MaxPooling2D(pool_size=(2, 2))) 
          
        model.add(Conv2D(32, (2, 2))) 
        model.add(Activation('relu')) 
        model.add(MaxPooling2D(pool_size=(2, 2))) 
          
        model.add(Conv2D(64, (2, 2))) 
        model.add(Activation('relu')) 
        model.add(MaxPooling2D(pool_size=(2, 2))) 
          
        model.add(Flatten()) 
        model.add(Dense(64)) 
        model.add(Activation('relu')) 
        model.add(Dropout(0.5)) 
        model.add(Dense(1)) 
        model.add(Activation('sigmoid'))

        model.compile(loss='binary_crossentropy', 
                      optimizer='rmsprop', 
                      metrics=['accuracy']) 
        model.load_weights(model_file)
        self.model = model
        self.graph = tf.get_default_graph()

    def analyze_picture(self, image_file):
        if not self.model:
            return -1
        test = image.load_img(image_file, target_size=(500, 375))
        test = image.img_to_array(test)
        test = np.expand_dims(test, axis = 0)
        with self.graph.as_default():
            result = self.model.predict(test)
        return result[0][0]

