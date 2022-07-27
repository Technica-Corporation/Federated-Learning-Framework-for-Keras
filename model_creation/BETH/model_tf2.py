import os, argparse, pickle
import pandas as pd
import numpy as np
import tensorflow as tf
import logging
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import f1_score, confusion_matrix
from preprocess import prepare_dataset

logging.basicConfig(level = logging.INFO)

def autoencoder(dim_in = 7, enc_dims = [4,2]):
    dec_dims = enc_dims[:-1]
    dec_dims.reverse()
    dims = enc_dims + dec_dims 
    input_layer = tf.keras.Input(shape=(dim_in,))
    h = input_layer
    for l in dims:
        h = tf.keras.layers.Dense(l, activation='sigmoid')(h)
    output_layer = tf.keras.layers.Dense(dim_in, activation='sigmoid')(h)
    model = tf.keras.Model(input_layer, output_layer)
#    optimizer = tf.keras.optimizers.Adam(0.00000001)
    model.compile(optimizer='adam', loss='mean_squared_error')
    # print(model.summary())
    return model

def create_scaler(df, scaler_file):
    feats, labels = prepare_dataset(df)
    scaler = MinMaxScaler()
    scaler.fit(feats)
    print(f"Finished with scalar. Writing to {scaler_file}")
    pickle.dump( scaler, open( scaler_file, 'wb' ) )
    
def train(df, scaler, epochs, model_output_path):
    # checkpoint_path = "model.ckpt"
    # checkpoint_dir = os.path.dirname(checkpoint_path)
    # cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
    #                                              save_weights_only=True,
    #                                              verbose=1)
    feats, labels = prepare_dataset(df, scaler = scaler)
    model = autoencoder(dim_in = feats.shape[1])
    model.fit(feats, feats, batch_size=32, epochs=epochs, verbose=1) #, callbacks=[cp_callback])
    logging.info(f"Finished training model. Writing to {model_output_path}")
    for layer in model.layers:
        print(layer.weights)
    model.save(f'{model_output_path}/model.h5')
    return model

def test(model, df, scaler, th_perc = 90):
    feats, labels = prepare_dataset(df, scaler = scaler)
    preds = model.predict(feats)
    loss_func = tf.keras.metrics.MeanSquaredError()
    losses = [ loss_func(pred, target) for pred, target in zip(preds,feats) ]
    threshold = np.percentile(losses, th_perc)
    preds = (losses > threshold) * 1
    
    # Statistics
    logging.info("Mean: ", np.mean(losses))
    logging.info("non-Sus Mean:", np.sum(losses*(1-labels)) / np.sum(1-labels), np.sum(1-labels))
    logging.info("Sus Mean:", np.sum(losses*labels) / np.sum(labels), np.sum(labels))

    # logging.info(np.sum(preds), '/', np.sum(train_labels))
    logging.info("threshold:", threshold)
    logging.info(f1_score(labels, preds))
    logging.info(confusion_matrix(labels,preds))

def load_csvfolder(folder):
    dfs = []
    for f in [os.path.join(folder, x) for x in os.listdir(folder) if x.endswith('.csv')]:
        dfs.append(pd.read_csv(f))
    return pd.concat(dfs, axis='index', ignore_index=True) 
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--scaler', default=None, type=str, help = 'path to scaler file')
    parser.add_argument('-sd', '--scaler_data', default=None, type=str, help = 'path to scaler data')
    parser.add_argument('-td', '--train_data', default=None, type=str, help="path to training data")
    parser.add_argument('-e', '--epochs', default=10, type=int, help="number of training epochs")
    parser.add_argument('-m', '--model_output_path', default=None, type=str, help="Path to write the model to")
    parser.add_argument('-t', '--test', default=False, action='store_true')
    args = parser.parse_args()
    
    assert(args.scaler)
    
    if args.scaler_data:
        df = load_csvfolder(args.scaler_data)
        create_scaler(df, args.scaler)
        
    if args.train_data:
        logging.info("Loading Training Data")
        df = load_csvfolder(args.train_data)
        with open(args.scaler, 'rb') as pickle_file:
            scaler = pickle.load(pickle_file)
        model = train(df=df, scaler=scaler, epochs = args.epochs, model_output_path = args.model_output_path)
        if args.test:
            test(model, df, scaler)            

