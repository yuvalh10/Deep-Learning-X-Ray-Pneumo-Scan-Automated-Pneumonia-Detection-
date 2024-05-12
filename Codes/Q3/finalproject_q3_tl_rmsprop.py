# -*- coding: utf-8 -*-
"""FinalProject Q3- TL-RMSprop

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1j8P1TJSYRuES9_5Tjy4kCe6jMdBCGSnb

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
from tensorflow.keras.models import Model
from tensorflow.keras import datasets, layers, optimizers
from tensorflow.keras.layers import Dropout,GlobalAveragePooling2D, Dense
from matplotlib import pyplot as plt
from tensorflow.keras.optimizers import Adagrad
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import precision_score, recall_score,f1_score
from sklearn.metrics import auc
from tensorflow.keras.applications import MobileNetV2

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
    # Normalize the pixels on every image and label
    normal = []
    labels = []

    for im_path,label in data:
        # Assigning labels based on the type of pneumonia
        if label == 2:
            labels.append(1)  # Label 1 for bacteria pneumonia
        else:
            labels.append(label)

       # Open the image and convert it to RGB
        image = Image.open(im_path).convert("RGB")

        # Resize the image to 180x180
        resized_image = image.resize((180, 180))

        # Convert the resized image to a NumPy array
        image_array = np.array(resized_image)

        # Normalize the pixel values
        im_normal = image_array / 255.0

        normal.append(im_normal)

    return np.array(normal), np.array(labels)

def CreatingtVal(val):
    val_norm, val_label = NormalPixels(val)  # Normalize validation data
    return val_norm, val_label

def CreatingtTrain(train):
    train_norm, train_label = NormalPixels(train)  # Normalize training data
    return train_norm, train_label

def CreatingtTest(test):
    test_norm, test_label = NormalPixels(test)  # Normalize test data
    return test_norm, test_label

val_norm, val_label = CreatingtVal(val)
train_norm, train_label = CreatingtTrain(train)
test_norm, test_label = CreatingtTest(test)

"""# Building the Transfer Learning model"""

# Build the model
test_accs = []
test_loss_accs = []
epochs = [50,80]
learning_rates = [0.001]

for lr in learning_rates:
  for epoch in epochs:
        print(f"Training CNN with SGD: learning rate: {lr}, epochs: {epoch}")
        base_model = tf.keras.applications.MobileNetV2(input_shape=(180, 180, 3), include_top=False, weights='imagenet', input_tensor=None, pooling=None, classes=None)
        base_model.trainable = False

        preprocess_input = tf.keras.applications.mobilenet_v2.preprocess_input
        global_average_layer = tf.keras.layers.GlobalAveragePooling2D()
        prediction_layer = tf.keras.layers.Dense(1, activation='sigmoid')

        inputs = tf.keras.Input(shape=(180, 180, 3))
        x = preprocess_input(inputs)
        x = base_model(x, training=False)

        # Additional layers
        x = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same')(x)
        x = tf.keras.layers.MaxPooling2D((2, 2))(x)
        x = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
        x = tf.keras.layers.MaxPooling2D((2, 2))(x)
        x = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)

        x = global_average_layer(x)
        x = tf.keras.layers.Dropout(0.1)(x)
        outputs = prediction_layer(x)

        transfer_learning = tf.keras.Model(inputs, outputs)

        # Compile the model
        transfer_learning.compile(optimizer=tf.keras.optimizers.RMSprop(learning_rate=lr),
                           loss=tf.keras.losses.BinaryCrossentropy(from_logits=False),
                           metrics=['accuracy'])

        history = transfer_learning.fit(train_norm, train_label, epochs=epoch, batch_size=20,
                                validation_data=(val_norm, val_label), verbose=1)

        transfer_learning.summary()

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
        test_loss, test_acc = transfer_learning.evaluate(test_norm, test_label, verbose=1)
        print("\nTest accuracy: ", test_acc)
        print("\nTest loss: ", test_loss)

# Get the predicted probabilities for the test set
predicted_probabilities = transfer_learning.predict(test_norm)

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

threshold = 0.1+0.05*(len(f1_values)-(max_index+1))

print(f"The best F1 score is {max_f1:.3} with threshold of {threshold:.2}")

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
test_loss, test_acc = transfer_learning.evaluate(test_norm, test_label, verbose=1)
print("\nTest accuracy: ", test_acc)
print("\nTest loss: ", test_loss)

# Get the predicted probabilities for the test set
predicted_probabilities = transfer_learning.predict(test_norm)

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

threshold = 0.1+0.05*(len(f1_values)-(max_index+1))

print(f"The best F1 score is {max_f1:.3} with threshold of {threshold:.2}")