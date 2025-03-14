from dagster import asset, AssetIn, Int, Float, multi_asset, AssetOut, AssetKey
import pandas as pd
from sklearn.model_selection import train_test_split

@multi_asset(
    ins={
        "scores_users_movies": AssetIn()
    },
    outs={
        "preprocessed_training_data": AssetOut(),
        "user2Idx": AssetOut(),
        "movie2Idx": AssetOut(),
    }
)
def preprocessed_data(scores_users_movies: pd.DataFrame):
    u_unique = scores_users_movies.user_id.unique()
    user2Idx = {o:i+1 for i,o in enumerate(u_unique)}
    m_unique = scores_users_movies.movie_id.unique()
    movie2Idx = {o:i+1 for i,o in enumerate(m_unique)}
    scores_users_movies['encoded_user_id'] = scores_users_movies.user_id.apply(lambda x: user2Idx[x])
    scores_users_movies['encoded_movie_id'] = scores_users_movies.movie_id.apply(lambda x: movie2Idx[x])

    preprocessed_training_data = scores_users_movies.copy()
    print("Columns preprocessed_data:", list(preprocessed_training_data.columns))
    return preprocessed_training_data, user2Idx, movie2Idx


@multi_asset(
    ins={
        "preprocessed_training_data": AssetIn(key=AssetKey("preprocessed_training_data")
        )
    },
    outs={
        "X_train": AssetOut(),
        "X_test": AssetOut(),
        "y_train": AssetOut(),
        "y_test": AssetOut(),
    }
)
def split_data(context, preprocessed_training_data:pd.DataFrame):
    context.log.info(f"columns in: {preprocessed_training_data.columns}")
    test_size=0.10
    random_state=42
    X = preprocessed_training_data[['user_id', 'movie_id']]
    y = preprocessed_training_data['rating']
    X_train, X_test, y_train, y_test = train_test_split(X, y,
        test_size=test_size, random_state=random_state
    )
    return X_train, X_test, y_train, y_test


@multi_asset(
    required_resource_keys={'mlflow'},
    ins={
        "X_train": AssetIn(),
        "y_train": AssetIn(),
        "user2Idx": AssetIn(),
        "movie2Idx": AssetIn(),
    },
    outs={"model_trained": AssetOut(io_manager_key="keras_io_manager")},
    config_schema={
        'batch_size': Int,
        'epochs': Int,
        'learning_rate': Float,
        'embeddings_dim': Int
    }
)
def model_trained(context, X_train, y_train, user2Idx, movie2Idx):
    from .model_helper import get_model
    from keras.optimizers import Adam
    mlflow = context.resources.mlflow
    mlflow.log_params(context.op_config)
    mlflow.tensorflow.autolog()


    batch_size = context.op_config["batch_size"]
    epochs = context.op_config["epochs"]
    learning_rate = context.op_config["learning_rate"]
    embeddings_dim = context.op_config["embeddings_dim"]

    model = get_model(len(movie2Idx), len(user2Idx), embeddings_dim)

    model.compile(Adam(learning_rate=learning_rate), 'mean_squared_error')

    context.log.info(f'batch_size: {batch_size} - epochs: {epochs}')
    history = model.fit(
        [
            X_train.user_id,
            X_train.movie_id
        ],
        y_train.rating,
        batch_size=batch_size,
        epochs=epochs,
        verbose=1
    )
    for i, l in enumerate(history.history['loss']):
        mlflow.log_metric('mse', l, i)
    from matplotlib import pyplot as plt
    fig, axs = plt.subplots(1)
    axs.plot(history.history['loss'], label='mse')
    plt.legend()
    mlflow.log_figure(fig, 'plots/loss.png')
    return model

@multi_asset(
    required_resource_keys={'mlflow'},
    ins={"model_trained": AssetIn()},
    outs={"model_stored": AssetOut()}
)
def log_model(context, model_trained):
    import numpy as np
    mlflow = context.resources.mlflow
    context.log.info(f"Tipo de model_trained: {type(model_trained)}")
    logged_model = mlflow.tensorflow.log_model(
        model_trained,
        "keras_dot_product_model",
        registered_model_name='keras_dot_product_model',
    )

    model_stored = {
        'model_uri': logged_model.model_uri,
        'run_id': logged_model.run_id
    }
    return model_stored


@asset(
    required_resource_keys={'mlflow'},
    ins={
        "model_trained": AssetIn(),
        "X_test": AssetIn(),
        "y_test": AssetIn(),
    }
)
def evaluate_model(context, model_trained, X_test:pd.DataFrame, y_test:pd.DataFrame):
    from sklearn.metrics import mean_squared_error

    mlflow = context.resources.mlflow

    # Hacer predicciones con el modelo cargado
    y_pred = model_trained.predict([
        X_test.user_id,
        X_test.movie_id
    ])

    # Calcular el error cuadrático medio (MSE)
    mse = mean_squared_error(y_pred.reshape(-1), y_test.rating.values)

    # Registrar las métricas en MLflow
    with mlflow.start_run(nested=True):
        mlflow.log_metrics({
            'test_mse': mse,
            'test_rmse': mse**(0.5)
        })

    context.log.info(f"Evaluación completada - MSE: {mse}, RMSE: {mse**(0.5)}")
