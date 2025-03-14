

mlflow_resource_config = {
        'experiment_name': 'recommender_system',
        "mlflow_tracking_uri": "http://localhost:5000",
}

dbt_resources = {
    'dbt': {
        'config': {
            'project_dir': '/home/bajiks/code/Bajiks/ITBA/final-project/recommender_system/recommender_system/db_postgres',
        }
    }
}


job_data_config = {
    'resources': {
        'mlflow': {
            'config': mlflow_resource_config,
            },
    },
    'ops': {

    }
}

training_config = {
    'model_trained': {
        'config': {
            'batch_size': 128,
            'epochs': 10,
            'learning_rate': 1e-3,
            'embeddings_dim': 5
        }
    }
}

job_dbt_config = {
    'resources': {
        'dbt': dbt_resources['dbt'],
    }
}

job_training_config = {
    'resources': {
        'mlflow': {
            'config': mlflow_resource_config,
            },
    },
    'ops': {
        **training_config
    }
}
