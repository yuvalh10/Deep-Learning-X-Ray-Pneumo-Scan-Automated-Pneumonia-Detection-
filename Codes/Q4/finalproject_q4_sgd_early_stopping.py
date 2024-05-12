# -*- coding: utf-8 -*-
"""FinalProject Q4-SGD-Early Stopping

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1F7bHWZbXQuQOQrT3I0D6tXHpZZ3FuOHZ

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
from tensorflow.keras.layers import Dropout, BatchNormalization,Dense
from matplotlib import pyplot as plt
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adagrad
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import precision_score, recall_score,f1_score
from sklearn.metrics import auc
from keras.callbacks import EarlyStopping

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
#val = virus[:300] + bacteria[:556] + healthy[:316]
#test = virus[300:600] + bacteria[556:1112] + healthy[316:632]
#train = virus[600:] + bacteria[1112:] + healthy[632:]

val = virus[:25] + bacteria[:25] + healthy[:50]
test = virus[25:325] + bacteria[25:550] + healthy[25:350]
train = virus[325:] + bacteria[550:] + healthy[350:]

def NormalPixels(data):
    # normalizing the pixels i=on every image and label
    normal = []
    labels = []

    for im_path,label in data:
        image = Image.open(im_path)
        rgb_data = image.convert("L").getdata() # gets grayscale image
        resized_image = rgb_data.resize((180,180))
        image_array = np.reshape(resized_image,(180,180)) # Convert the image to a NumPy array
        im_normal = image_array / 255.0 # normalizing
        normal.append(im_normal)
        labels.append(label)

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

test_label = tf.keras.utils.to_categorical(test_label)
train_label = tf.keras.utils.to_categorical(train_label)
val_label = tf.keras.utils.to_categorical(val_label)

"""# Building the CNN model"""

# Build the model
test_accs = []
test_loss_accs = []
epochs = [60]
learning_rates = [0.0005]

for lr in learning_rates:
  for epoch in epochs:
        print(f"Training CNN with SGD: learning rate: {lr}, epochs: {epoch}")
        CNN = models.Sequential()

        CNN.add(layers.Conv2D(32, (3, 3), padding = 'same' ,activation='relu', input_shape=(180, 180, 1)))
        CNN.add(BatchNormalization())
        CNN.add(layers.MaxPooling2D((2,2) , strides = 2 , padding = 'same'))
        CNN.add(layers.Conv2D(64 , (3,3) , strides = 1 , padding = 'same' , activation = 'relu'))

        CNN.add(layers.MaxPooling2D((2,2) , strides = 2 , padding = 'same'))
        CNN.add(layers.Conv2D(64 , (3,3) , strides = 1 , padding = 'same' , activation = 'relu'))
        CNN.add(Dropout(0.1))
        CNN.add(BatchNormalization())

        CNN.add(layers.MaxPooling2D((2,2) , strides = 2 , padding = 'same'))
        CNN.add(layers.Conv2D(64 , (3,3) , strides = 1 , padding = 'same' , activation = 'relu'))
        CNN.add(BatchNormalization())

        CNN.add(layers.MaxPooling2D((2,2) , strides = 2 , padding = 'same'))
        CNN.add(layers.Conv2D(128 , (3,3) , strides = 1 , padding = 'same' , activation = 'relu'))
        CNN.add(Dropout(0.2))
        CNN.add(BatchNormalization())

        CNN.add(layers.MaxPooling2D((2,2) , strides = 2 , padding = 'same'))
        CNN.add(layers.Conv2D(256 , (3,3) , strides = 1 , padding = 'same' , activation = 'relu'))
        CNN.add(Dropout(0.2))
        CNN.add(BatchNormalization())

        CNN.add(layers.MaxPooling2D((2,2) , strides = 2 , padding = 'same'))

        CNN.add(layers.Flatten())

        CNN.add(layers.Dense(3, activation='softmax'))

        # Compile the model
        CNN.compile(optimizer = optimizers.SGD(learning_rate=lr),
                    loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True), metrics=['accuracy'])

        CNN.summary()
        # Define early stopping callback
        early_stopping = EarlyStopping(monitor='val_loss', patience=15 ,mode='min', verbose=1, restore_best_weights=True)

        history = CNN.fit(train_norm, train_label, epochs = epoch, batch_size = 20,
                            validation_data=(val_norm, val_label), verbose=1,callbacks=[early_stopping])
        # Evaluate the model on the test set
        test_loss, test_acc = CNN.evaluate(test_norm, test_label, verbose=1)
        test_accs.append((test_acc,f' Learning Rate: {lr}, Epochs: {epoch}'))
        test_loss_accs.append((test_loss,f'Learning Rate: {lr}, Epochs: {epoch}'))
        print("\nTest accuracy: ", test_acc)
        print("\nTest loss: ", test_loss)
        plt.plot(history.history['accuracy'], label='Training Accuracy')
        plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
        plt.title(f'Training and Validation Accuracy vs. Number of Epochs\nOptimizer: Optimizer:SGD, Learning Rate: {lr}, Epochs: {epoch}')
        plt.xlabel('Epochs')
        plt.ylabel('Accuracy')
        plt.grid()
        plt.legend(loc='lower right')
        plt.show()

        plt.clf() # clear figure
        plt.plot(history.history['loss'], label='Training loss')

        plt.plot(history.history['val_loss'], label='Validation loss')
        plt.title(f'Training and Validation Loss vs. Number of Epochs\nOptimizer:SGD, Learning Rate: {lr}, Epochs: {epoch}')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.grid()
        plt.legend(loc='upper right')
        plt.show()

"""# plot loss and accuracy for the train and validation set"""

# Get the predicted probabilities for the test set
predicted_probabilities = CNN.predict(test_norm)
predicted_labels = np.argmax(predicted_probabilities, axis=-1)
true_labels = np.argmax(test_label, axis=-1)

# Generate the confusion matrix
conf_matrix = confusion_matrix(true_labels, predicted_labels)

# Plot the confusion matrix
plt.figure(figsize=(12, 8))
sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues", cbar=False)
plt.xticks(ticks=np.arange(3) + 0.5, labels=['Healthy','Virus', 'Bacteria'])
plt.yticks(ticks=np.arange(3) + 0.5, labels=['Healthy','Virus', 'Bacteria'])
plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.title('Confusion Matrix')
plt.show()

# Calculate True Positives, False Positives, and False Negatives
TP = np.diag(conf_matrix)
FP = np.sum(conf_matrix, axis=0) - TP
FN = np.sum(conf_matrix, axis=1) - TP

# Calculate precision
precision = TP / (TP + FP)

# Calculate recall
recall = TP / (TP + FN)

# Print precision and recall for each class
for i in range(len(precision)):
    print(f"Class {i}: Precision = {precision[i]:.4f}, Recall = {recall[i]:.4f}")