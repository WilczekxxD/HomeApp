import tensorflow
from tensorflow import keras
import numpy as np

model = keras.Sequential()
model.add(keras.layers.Embedding())