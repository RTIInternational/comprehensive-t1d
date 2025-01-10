import copy

import pandas as pd
import os
from src.custom import custom_populations, custom_populations_psa

INPUT_DIR = os.path.join('data')
OUTPUT_DIR = os.path.join('src', 'population', 'output')


def make_directory(directory_path):
    """
    Create an output directory as applicable.

    :param directory_path: Directory path
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


class PopulationBuilder:
    def __init__(self, scenario_tuple, uuid):

        self.scenario_tuple = scenario_tuple
        # scenarios with shared data sets follow the same non-intervention/intervention pattern
        self.non_intervention_scenario = scenario_tuple[0]
        self.seed = self.non_intervention_scenario['seed']
        self.scenario_name = self.non_intervention_scenario['scenario_name']
        self.equation_set = self.non_intervention_scenario['diabetes_type']
        self.population_size = self.non_intervention_scenario['size']

        self.population_output_dir = os.path.join(OUTPUT_DIR, str(uuid))
        make_directory(self.population_output_dir)

    def build_population(self):
        """
        Build a population by running raw data through the processing pipeline.
        """
        if self.non_intervention_scenario['scenario_type'] == 'PSA':
            population_dataset_uuid = self.non_intervention_scenario['population_dataset_uuid']
            if population_dataset_uuid and population_dataset_uuid != 'none':
                shared_df = pd.read_csv(population_dataset_uuid)
                # don't delete; used for testing
                # shared_df = pd.read_csv('data/default-populations/prediabetes_nhanes_screening.csv')
                # shared_df = pd.read_csv('data/default-populations/prediabetes_nhanes.csv')
                # shared_df = pd.read_csv('data/default-populations/t2d_nhanes.csv')
                # shared_df = pd.read_csv('data/default-populations/t1d_search-exchange.csv')
                # shared_df = pd.read_csv('data/default-populations/t1d_connolly_USdataformat1.csv')
                # shared_df = pd.read_csv('data/default-populations/Connolly_t1d_csv.csv')
                shared_df = shared_df.dropna()
                df_dict = custom_populations_psa_shared.generate_custom_population(self.seed, self.scenario_tuple,
                                                                               self.equation_set, shared_df)
            else:
                df_dict = custom_populations_psa.generate_custom_population(self.seed, self.scenario_tuple, self.equation_set)
        # standard run
        else:
            # a user has decided to use a shared population data set; get the correct path and load the population
            population_dataset_uuid = self.non_intervention_scenario['population_dataset_uuid']
            if population_dataset_uuid and population_dataset_uuid != 'none':
                shared_df = pd.read_csv(population_dataset_uuid)
                # don't delete; used for testing
                # shared_df = pd.read_csv('data/default-populations/prediabetes_nhanes_screening.csv')
                # shared_df = pd.read_csv('data/default-populations/t2d_nhanes.csv')
                # shared_df = pd.read_csv('data/default-populations/t2d_nhanes_bariatric_surgery.csv')
                # shared_df = pd.read_csv('data/default-populations/t2d_accord.csv')
                # shared_df = pd.read_csv('data/default-populations/t2d_lookahead_accord.csv')
                # shared_df = pd.read_csv('data/default-populations/prediabetes_nhanes.csv')
                # shared_df = pd.read_csv('data/default-populations/prediabetes_aric.csv')
                # shared_df = pd.read_csv('data/default-populations/Connolly_t1d_csv.csv')
                # shared_df = pd.read_csv('data/default-populations/t1d_search-exchange.csv')
                # shared_df = pd.read_csv('data/default-populations/t1d_connolly_USdataformat1.csv')
                if 'seqn' in shared_df.columns:
                    shared_df = shared_df.drop('seqn', axis=1)
                # make sure no row contains nan values = data set must be complete!
                shared_df = shared_df.dropna()
                df_dict = custom_populations_shared.generate_custom_population(self.seed, self.scenario_tuple,
                                                                        self.equation_set, shared_df)
            else:
                df_dict = custom_populations.generate_custom_population(self.seed, self.scenario_tuple,
                                                                        self.equation_set)

        # non-intervention and intervention population need to match
        # generate and write intervention population first; then write non-intervention population
        for output_name, df in df_dict.items():
            self.write_population(df, output_name)

    def load_df(self, population_name):
        """
        Read raw data into memory
        """
        return pd.read_csv(os.path.join(INPUT_DIR, f'{population_name}.csv'))

    def sample(self, presample_df):
        """
        Sample a given dataframe to the appropriate size (as specified in the
        scenario file)
        """
        weights = None
        if self.equation_set == 'ukpds':
            weights = presample_df['int_weights_q']

        if "not_sampled" in self.scenario_name:
            presample_df.set_index([[i for i in range(0, len(presample_df))]], inplace=True)
            presample_df.index.rename('id', inplace=True)
            presample_df.reset_index(inplace=True)
            return presample_df
        sampled_df = presample_df.sample(n=self.population_size, replace=True,
                                         weights=weights,
                                         random_state=self.seed)

        sampled_df.set_index([[i for i in range(0, len(sampled_df))]], inplace=True)
        sampled_df.index.rename('id', inplace=True)
        sampled_df.reset_index(inplace=True)
        return sampled_df

    def write_population(self, df, output_name):
        """
        Write a final dataframe to disk
        """
        try:
            # df.to_csv(os.path.join(self.population_output_dir, f'{output_name}.csv'), index=False)
            # df.to_pickle(os.path.join(self.population_output_dir, f'{output_name}.pkl'))
            df.to_parquet(f"{self.population_output_dir}/{output_name}.parquet")
        except IOError as e:
            print(f"An I/O error occurred while writing the CSV file: {e}")
