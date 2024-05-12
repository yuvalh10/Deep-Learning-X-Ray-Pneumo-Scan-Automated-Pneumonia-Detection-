# -*- coding: utf-8 -*-
"""FinalProject Q1 - CNN

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1wCaZ3yu0zDN_4g-CoL4GJtTRH8pw7cuw

# Import Libraries and Modules
"""

import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import os
import random
import re
import seaborn as sns
from sklearn.metrics import confusion_matrix
from zipfile import ZipFile
from glob import glob
from google.colab import drive
from keras.models import Sequential
from PIL import Image
from tensorflow.keras import datasets, layers, models, optimizers
from tensorflow.keras.layers import Dropout
from matplotlib import pyplot as plt
from tensorflow.keras.optimizers import Adagrad
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import precision_score, recall_score,f1_score
from sklearn.metrics import auc

"""# Extract the images and clasiffing into 3 categories
# (healthy, virus, bacterial)
"""

drive.mount('/content/drive')

file_name = '/content/drive/My Drive/Final Project DL & ML/chest-xray.zip'

with ZipFile(file_name, 'r') as zip_file:
  zip_file.extractall()  # Extract all contents of the ZIP file.
  print('Done')

train_path = '/content/chest_xray/chest_xray/train'
val_path = '/content/chest_xray/chest_xray/val'
test_path = '/content/chest_xray/chest_xray/test'

pre_path = '/content/chest_xray/chest_xray/'

# Define paths for different sets and classes.
train_normal_dir = pre_path + 'train/NORMAL/'
train_pneu_dir = pre_path + 'train/PNEUMONIA/'

test_normal_dir = pre_path + 'test/NORMAL/'
test_pneu_dir = pre_path + 'test/PNEUMONIA/'

val_normal_dir = pre_path + 'val/NORMAL/'
val_pneu_dir = pre_path + 'val/PNEUMONIA/'


#initiazing the healthy, bacteria and virus cases of the images
virus = [] #1493 images total
bacteria = [] #2780 images total
healthy = [] #1583 images total

healthy += glob(train_normal_dir + '*jpeg')

#By using Regular Expressions we sorting the cases properly
#0- healthy, 1- virus case, 2 - bacteria case
for i in os.listdir(train_pneu_dir):
  if(re.search("virus.*jpeg", i)):
      virus.append([train_pneu_dir+i,1])
  elif(re.search("bacteria.*jpeg", i)):
      bacteria.append([train_pneu_dir+i,2])

healthy += glob(test_normal_dir + '*jpeg')

for i in os.listdir(test_pneu_dir):
  if(re.search("virus.*jpeg", i)):
      virus.append([test_pneu_dir+i,1])
  elif(re.search("bacteria.*jpeg", i)):
      bacteria.append([test_pneu_dir+i,2])

healthy += glob(val_normal_dir + '*jpeg')

for i in os.listdir(val_pneu_dir):
  if(re.search("virus.*jpeg", i)):
      virus.append([val_pneu_dir+i,1])
  elif(re.search("bacteria.*jpeg", i)):
      bacteria.append([val_pneu_dir+i,2])

for i in range(len(healthy)):
  healthy[i]=(healthy[i],0)

for lst in [healthy,virus,bacteria]:
  random.shuffle(lst)

"""# Creating the test, train and validation sets"""

# 20% validation and test sets, 60% train set from all data
# Splitting data into train, validation, and test sets
val = virus[:300] + bacteria[:556] + healthy[:316]


test = virus[300:600] + bacteria[556:1112] + healthy[316:632]
train = virus[600:] + bacteria[1112:] + healthy[632:]

def NormalPixels(data):
    # normalizing the pixels i=on every image and label
    normal = []
    labels = []

    for im_path,label in data:
        #works only for Q1
        if label == 2:
            labels.append(1)
        else:
            labels.append(label)
        image = Image.open(im_path)
        rgb_data = image.convert("L").getdata() # gets grayscale image
        resized_image = rgb_data.resize((180,180))
        image_array = np.reshape(resized_image,(180,180)) # Convert the image to a NumPy array
        im_normal = image_array / 255.0 # normalizing
        normal.append(im_normal)

    return np.array(normal),np.array(labels)

def CreatingtVal(val):
    val_norm, val_label = NormalPixels(val)  # Normalize validation data
    return val_norm, val_label

def CreatingtTrain(train):
    train_norm, train_label = NormalPixels(train)  # Normalize training data
    return train_norm, train_label

def CreatingtTest(test):
    test_norm, test_label = NormalPixels(test)  # Normalize test data
    return test_norm, test_label

# Load and preprocess the data
val_norm, val_label = CreatingtVal(val)
train_norm, train_label = CreatingtTrain(train)
test_norm, test_label = CreatingtTest(test)

"""# Building the CNN model"""

# Build the model
CNN = models.Sequential()

CNN.add(layers.Conv2D(32, (3, 3), padding = 'same' ,activation='relu', input_shape=(180, 180, 1)))
CNN.add(layers.MaxPooling2D((2,2) , strides = 2 , padding = 'same'))
CNN.add(layers.Conv2D(64 , (3,3) , strides = 1 , padding = 'same' , activation = 'relu'))

CNN.add(layers.MaxPooling2D((2,2) , strides = 2 , padding = 'same'))
CNN.add(layers.Conv2D(64 , (3,3) , strides = 1 , padding = 'same' , activation = 'relu'))
CNN.add(Dropout(0.1))

CNN.add(layers.MaxPooling2D((2,2) , strides = 2 , padding = 'same'))
CNN.add(layers.Conv2D(64 , (3,3) , strides = 1 , padding = 'same' , activation = 'relu'))

CNN.add(layers.MaxPooling2D((2,2) , strides = 2 , padding = 'same'))
CNN.add(layers.Conv2D(128 , (3,3) , strides = 1 , padding = 'same' , activation = 'relu'))
CNN.add(Dropout(0.2))

CNN.add(layers.MaxPooling2D((2,2) , strides = 2 , padding = 'same'))
CNN.add(layers.Conv2D(256 , (3,3) , strides = 1 , padding = 'same' , activation = 'relu'))
CNN.add(Dropout(0.2))

CNN.add(layers.MaxPooling2D((2,2) , strides = 2 , padding = 'same'))

CNN.add(layers.Flatten())
CNN.add(Dropout(0.2))
CNN.add(layers.Dense(1, activation = 'sigmoid'))

# Compile the model
CNN.compile(optimizer = Adagrad(learning_rate=0.01),
            loss='binary_crossentropy',
            metrics=['accuracy'])

CNN.summary()

history = CNN.fit(train_norm, train_label, epochs = 10, batch_size = 20,
                    validation_data=(val_norm, val_label), verbose=1)

"""# plot loss and accuracy for the train and validation set"""

plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Training and Validation Accuracy vs. Number of Epochs')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.grid()
plt.legend(loc='lower right')
plt.show()

plt.clf() # clear figure
plt.plot(history.history['loss'], label='Training loss')

plt.plot(history.history['val_loss'], label='Validation loss')
plt.title('Training and validation loss vs. Number of Epochs')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.grid()
plt.legend(loc='upper right')
plt.show()

# Evaluate the model on the test set
test_loss, test_acc = CNN.evaluate(test_norm, test_label, verbose=1)
print("\nTest accuracy: ", test_acc)
print("\nTest loss: ", test_loss)

# Get the predicted probabilities for the test set
predicted_probabilities = CNN.predict(test_norm)

# Convert probabilities to binary predictions (0 or 1)
predicted_labels = (predicted_probabilities > 0.5).astype(int)

# Generate the confusion matrix
conf_matrix = confusion_matrix(test_label, predicted_labels)

# Plot the confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues", cbar=False)
# Set labels for the axes
plt.xticks(ticks=[0.5, 1.5], labels=['Healthy', 'Sick'])
plt.yticks(ticks=[0.5, 1.5], labels=['Healthy', 'Sick'])

plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.title('Confusion Matrix')
plt.show()

precision, recall, _ = precision_recall_curve(test_label,predicted_labels)

precision_values = []
recall_values = []
f1_values = []

# Compute precision, recall, and threshold values for different thresholds
for threshold in np.arange(0.1, 0.95, 0.05):
    # Apply threshold to predicted probabilities
    predicted_labels = (predicted_probabilities > threshold)
    # Compute precision and recall
    precision = precision_score(test_label, predicted_labels)
    recall = recall_score(test_label, predicted_labels)
    f1 = f1_score(test_label, predicted_labels)
    precision_values.append(precision)
    recall_values.append(recall)
    f1_values.append(f1)

# Plot the precision-recall curve
plt.figure(figsize=(8, 6))
plt.plot(recall_values, precision_values,recall_values,precision_values,'ro')
for i in range(len(precision_values)):
  plt.text(recall_values[i],precision_values[i],f' f1={f1_values[i]:.3}',fontsize = 7, rotation = 20)
plt.xlabel('precision')
plt.ylabel('recall')
plt.title('Precision-Recall Curve')
plt.grid(True)
plt.show()

# Get the maximum number in the list
max_f1 = max(f1_values)

# Get the index of the maximum number
max_index = f1_values.index(max_f1)

threshold = 0.1+0.05*(max_index)

print(f"The best F1 score is {max_f1:.3} with threshold of {threshold:.2}")