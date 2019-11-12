import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow import keras
import tensorflow_datasets as tfds
from functools import partial


def rand_crop(image):
    shape = tf.shape(image)
    min_dim = tf.reduce_min([shape[0], shape[1]]) * 90 // 100
    return tf.image.random_crop(image, [min_dim, min_dim, 3])


def preprocess(image, label):
    cropped = rand_crop(image)
    cropped = tf.image.random_flip_left_right(cropped)
    resized_image = tf.image.resize(cropped, [299, 299])
    final_image = keras.applications.inception_v3.preprocess_input(resized_image)
    return final_image, label


dataset, info = tfds.load('tf_flowers', as_supervised=True, with_info=True)
base_model = keras.applications.inception_v3.InceptionV3(include_top=False, weights='imagenet')
n_classes = info.features['label'].num_classes
avg = keras.layers.GlobalAveragePooling2D()(base_model.output)
output = keras.layers.Dense(n_classes, activation='softmax')(avg)
model = keras.models.Model(inputs=base_model.input, outputs=output)
test_split, valid_split, train_split = tfds.Split.TRAIN.subsplit([10, 15, 75])
train_set_raw = tfds.load('tf_flowers', split=train_split, as_supervised=True)
valid_set_raw = tfds.load('tf_flowers', split=valid_split, as_supervised=True)
test_set_raw = tfds.load('tf_flowers', split=test_split, as_supervised=True)
dataset_size = info.splits['train'].num_examples
train_set = train_set_raw.shuffle(1000).repeat()
train_set = train_set.map(partial(preprocess)).batch(32).prefetch(1)
valid_set = valid_set_raw.map(preprocess).batch(32).prefetch(1)
test_set = test_set_raw.map(preprocess).batch(32).prefetch(1)

for layer in base_model.layers:
    layer.trainable = False

optimizer = keras.optimizers.SGD(lr=0.01, momentum=0.9, decay=0.01)
model.compile(loss='sparse_categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
history = model.fit(train_set, steps_per_epoch=int(0.75* dataset_size / 32), validation_data=valid_set,
                    validation_steps=int(0.15 * dataset_size / 32), epochs=2)
model.save('plantid_model')
keras.experimental.export_saved_model(history, 'plantid_savemodel')
