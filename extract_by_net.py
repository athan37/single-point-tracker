import tensorflow as tf
import numpy as np
from tensorflow import keras
from keras import layers
from skimage import io
import matplotlib.pyplot as plt
import cv2

vgg19 = keras.applications.VGG19(
    include_top=False,
    weights="imagenet",
)

vgg19.trainable = False

def feature_map_from(img_file):
    print("reach")
    image = cv2.imread(img_file)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (32, 32))
    image = np.expand_dims(image, axis=0) #Must have the batch
    image.shape

    image = vgg19.predict(image)
    plt.imshow(tf.reshape(image, (16, 32)))


feature_map_from('img_1.png')




