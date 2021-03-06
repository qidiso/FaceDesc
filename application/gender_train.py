# -*- coding: utf-8 -*-

import keras
import numpy as np
from keras.utils import np_utils
from sklearn.preprocessing import LabelEncoder

import prepare.dataset as dataset
from network.mobilenet import DepthwiseConv2D, relu6
from network.mobilenet import MobileNet
from network.xception import Xception


def augmented_train_mobilenet_with_data_generator(model_path):
    """
    To train a pre-trained model.
    :param model_path: pretrained model path.
    :return:
    """

    # STEPS_PER_EPOCH * BATCH_SIZE = DATA_SIZE
    EPOCH = 5
    DATA_SIZE = 100
    BATCH_SIZE = 20
    STEPS_PER_EPOCH = DATA_SIZE / BATCH_SIZE

    CLASS_NUM = 2

    INPUT_SHAPE = (224, 224)
    MODEL_PATH_EACH_EPOCH = '../model/gender/gender.mobilenet.augment.{epoch:02d}-{loss:.2f}.model'

    FINAL_MODEL_PATH = "../models/gender/gender.mobilenet.augment.final.model"

    checkpoint = keras.callbacks.ModelCheckpoint(MODEL_PATH_EACH_EPOCH, monitor='loss', verbose=1)

    model = keras.models.load_model(model_path,
                                    custom_objects={
                                    'relu6': relu6,
                                    'DepthwiseConv2D': DepthwiseConv2D
                                    })

    X_test, Y_test = dataset.load_data_from_config("../data/gender/gender_test.txt", input_shape=INPUT_SHAPE)

    encoder = LabelEncoder()
    encoder.fit(["F", "M"])
    encoded_Y_test = encoder.transform(Y_test).astype(np.int32)

    ohr_Y_test = np_utils.to_categorical(encoded_Y_test, CLASS_NUM)

    generator = dataset.data_generator("../data/gender/gender_train.txt",
                                       encoder,
                                       CLASS_NUM,
                                       input_shape=INPUT_SHAPE,
                                       batch_size=BATCH_SIZE)

    mobilenet = MobileNet(model)

    mobilenet.run_generator(
        generator,
        loss="categorical_crossentropy",
        optimizer="sgd",
        epoch=EPOCH,
        steps_per_epoch=STEPS_PER_EPOCH,
        val_data=(X_test, ohr_Y_test),
        augment=True,
        callbacks=[checkpoint]
    )

    mobilenet.save(FINAL_MODEL_PATH)


def train_mobilenet_with_data_generator():

    # STEPS_PER_EPOCH * BATCH_SIZE = DATA_SIZE
    EPOCH = 5
    DATA_SIZE = 100
    BATCH_SIZE = 20
    STEPS_PER_EPOCH = DATA_SIZE / BATCH_SIZE

    CLASS_NUM = 2

    INPUT_SHAPE = (224, 224)
    MODEL_PATH_EACH_EPOCH = '../model/gender/gender.mobilenet.{epoch:02d}-{loss:.2f}.model'
    FINAL_MODEL_PATH = '../models/gender/gender.mobilenet.final.model'

    checkpoint = keras.callbacks.ModelCheckpoint(MODEL_PATH_EACH_EPOCH, monitor='loss', verbose=1)
    tensorboard = keras.callbacks.TensorBoard(log_dir='../logs', histogram_freq=0, batch_size=8, write_graph=True, write_grads=False,
                                write_images=False, embeddings_freq=0, embeddings_layer_names=None,
                                embeddings_metadata=None)

    X_test, Y_test = dataset.load_data_from_config("../data/gender/gender_test.txt", input_shape=INPUT_SHAPE)

    encoder = LabelEncoder()
    encoder.fit(["F", "M"])
    encoded_Y_test = encoder.transform(Y_test).astype(np.int32)

    ohr_Y_test = np_utils.to_categorical(encoded_Y_test, CLASS_NUM)

    generator = dataset.data_generator("../data/gender/gender_train.txt",
                                       encoder,
                                       2,
                                       input_shape=INPUT_SHAPE,
                                       batch_size=BATCH_SIZE)

    net = MobileNet()
    net.build_network(include_top=True, input_shape=(224, 224, 3), output_shape=CLASS_NUM)
    net.run_generator(
        generator,
        loss="categorical_crossentropy",
        optimizer="sgd",
        epoch=EPOCH,
        steps_per_epoch=STEPS_PER_EPOCH,
        val_data=(X_test, ohr_Y_test),
        callbacks=[checkpoint, tensorboard]
    )

    net.save(FINAL_MODEL_PATH)

def train_mobilenet_with_keras_image_generator():
    # X_train, Y_train = dataset.load_data_from_config("../data/birth_label.txt")

    generator = dataset.get_keras_image_data_generator_from_directory(
        "C:/developer/dataset/gender_test/train/",
        target_size=(224, 224),
        # fit_x_train=X_train,
        batch_size=8,
        # zca_whitening=True,
        horizontal_flip=True,
        vertical_flip=True,
        samplewise_std_normalization=True,
        samplewise_center=True,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2
    )

    net = MobileNet()
    net.build_network(include_top=True, input_shape=(224, 224, 3), output_shape=5)
    net.run_generator(
        generator,
        loss="categorical_crossentropy",
        optimizer="sgd",epoch=1, steps_per_epoch=10
    )

    net.save_weights("../model/gender/gender.mobilenet.h5")


def run_xception():

    Y_train = dataset.load_labels("../data/gender/gender_label.txt")
    encoder = LabelEncoder()
    encoder.fit(Y_train)
    encoded_Y_train = encoder.transform(Y_train).astype(np.int32)

    ohr_Y_train = np_utils.to_categorical(encoded_Y_train, np.max(encoded_Y_train) + 1)

    net = Xception()
    net.build_network(include_top=True, input_shape=(299, 299, 3), output_shape=5)
    net.run_generator(
        dataset.get_keras_image_data_generator_from_directory(
            "C:/developer/dataset/gender_test/train/",
            target_size=(299, 299),
            zca_whitening=True,
            horizontal_flip=True,
            vertical_flip=True,
            samplewise_std_normalization=True,
            samplewise_center=True
        ),
        loss="categorical_crossentropy",
        optimizer="sgd"
    )

    net.save("../model/gender/gender.xception.h5")

if __name__ == "__main__":
    # run_mobilenet()
    # net = MobileNet()
    # net.build_network(include_top=True, input_shape=(224, 224, 3), output_shape=5)
    # keras.models.load_model("mobilenet.h5")


    # train_mobilenet_with_data_generator()
    train_mobilenet_with_data_generator()