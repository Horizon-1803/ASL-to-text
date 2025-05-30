# Importing the Keras libraries and packages
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Convolution2D
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Dense , Dropout
# from tensorflow.keras.layers import BatchNormalization

import os
import json
# from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau


os.environ["CUDA_VISIBLE_DEVICES"] = "1"
sz = 128
# Step 1 - Building the CNN

# Initializing the CNN
classifier = Sequential()

# First convolution layer and pooling
classifier.add(Convolution2D(32, (3, 3), input_shape=(sz, sz, 1), activation='relu'))
classifier.add(MaxPooling2D(pool_size=(2, 2)))
classifier.add(Dropout(0.3))
# Second convolution layer and pooling
classifier.add(Convolution2D(32, (3, 3), activation='relu'))
# input_shape is going to be the pooled feature maps from the previous convolution layer
classifier.add(MaxPooling2D(pool_size=(2, 2)))
# classifier.add(Dropout(0.3))
# classifier.add(Convolution2D(32, (3, 3), activation='relu'))
# input_shape is going to be the pooled feature maps from the previous convolution layer
# classifier.add(MaxPooling2D(pool_size=(2, 2)))

# Flattening the layers
classifier.add(Flatten())

# Adding a fully connected layer
classifier.add(Dense(units=128, activation='relu'))
classifier.add(Dropout(0.40))
classifier.add(Dense(units=96, activation='relu'))
classifier.add(Dropout(0.40))
classifier.add(Dense(units=64, activation='relu'))
classifier.add(Dense(units=26, activation='softmax')) # softmax for more than 2

# Compiling the CNN
classifier.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy']) # categorical_crossentropy for more than 2


# Step 2 - Preparing the train/test data and training the model
classifier.summary()
# Code copied from - https://keras.io/preprocessing/image/
from tensorflow.keras.preprocessing.image import ImageDataGenerator

train_datagen = ImageDataGenerator(
        rescale=1./255,
        # rotation_range=20,       # Add rotation
        # width_shift_range=0.2,    # Horizontal shift
        # height_shift_range=0.2,   # Vertical shift
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True)#,
        # vertical_flip=True,       # Add vertical flip
        # fill_mode='nearest')

test_datagen = ImageDataGenerator(rescale=1./255)

training_set = train_datagen.flow_from_directory('data2/train',
                                                 target_size=(sz, sz),
                                                 batch_size=20,
                                                 color_mode='grayscale',
                                                 class_mode='categorical')

test_set = test_datagen.flow_from_directory('data2/test',
                                            target_size=(sz , sz),
                                            batch_size=20,
                                            color_mode='grayscale',
                                            class_mode='categorical') 

from tensorflow.keras.callbacks import EarlyStopping
early_stopping = EarlyStopping(
    monitor='val_accuracy',  # Monitor validation accuracy
    patience=5,              # Wait for 5 epochs before stopping
    restore_best_weights=True  # Restore the best model weights
)

history = classifier.fit(
        training_set,
        steps_per_epoch=2102, # No of images in training set = 42049
        epochs=10,
        validation_data=test_set,
        validation_steps=307,# No of images in test set = 6145
        callbacks=[early_stopping],)

# Extracting the history values
training_accuracy = history.history['accuracy']
training_loss = history.history['loss']
validation_accuracy = history.history['val_accuracy'] 
validation_loss = history.history['val_loss']

# Saving the history to a JSON file
history_dict = {
    'training_accuracy': training_accuracy,
    'training_loss': training_loss,
    'validation_accuracy': validation_accuracy,
    'validation_loss': validation_loss
}

with open('training_history.json', 'w') as json_file:
    json.dump(history_dict, json_file)
    
# Saving the model
model_json = classifier.to_json()
with open("model-bw.json", "w") as json_file:
    json_file.write(model_json)
print('Model Saved')
classifier.save_weights('model-bw.weights.h5')
print('Weights saved')