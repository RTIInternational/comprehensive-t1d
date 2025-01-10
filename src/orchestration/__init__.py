import os
# import dataset
# from dotenv import load_dotenv
# load_dotenv()
#
BROADCAST_MESSAGES = {
    'configuration': 'Scenario Configured',
    'configuration_failed': 'Scenario Not Configured',
    'pending': 'Simulation Pending',
    'generation': 'Generating Population',
    'economics': 'Populating custom economics',
    'simulation': 'Running Simulation',
    'analysis': 'Analyzing Results',
    'executing': 'Executing',
    'done': 'Run Complete',
    'failed': 'Simulation Failed'
}

BROADCAST_STATUSES = {
    'error': 'Error',
    'message': 'Message'
}
#
#
BASE_ANALYSIS_PATH = os.path.join('src', 'analysis', 'output')
BASE_POPULATION_PATH = os.path.join('src', 'population', 'output')
BASE_SIMULATION_PATH = os.path.join('src', 'simulation', 'output')
#
#
LOGGING_FORMAT = '%(asctime)-15s %(message)s'
#
# user = os.getenv('POSTGRES_USER')
# pwd = os.getenv('POSTGRES_PWD')
# port = os.getenv('POSTGRES_PORT')
# host = os.getenv('POSTGRES_HOST')
# db_conn = 'postgresql://{user}:{password}@{host}:{port}/{name}'.format(
#     user=f'{user}', password=f'{pwd}', host=f'{host}', port=port, name=f'{user}'
# )
#
# sqlalchemy_kwargs = {
#     'pool_size': 10,
#     'max_overflow': 20,
#     'pool_timeout': 60,
# }
#
# DATABASE = dataset.connect(db_conn, engine_kwargs=sqlalchemy_kwargs)
