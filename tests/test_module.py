import json
import unittest
import os
from unittest.mock import patch

import pandas as pd
import openpe as pe
from openpe import Categories, Dataset

class TestModule(unittest.TestCase):

    categories = [
    #'modelo-de-gestión-documental-1479',
    #'alimentación-y-nutrición-32',
    'ciencia-y-tecnología-1136',
    #'energía-340',
    # 'covid-19-917',
    # 'agua-y-saneamiento-26',
    # 'desarrollo-urbano-339',
    # 'educación-28',
    # 'salud-27',
    # 'medio-ambiente-y-recursos-naturales-30',
    # 'transporte-25',
    # 'exprésate-perú-con-datos-1466',
    # 'desarrollo-social-338',
    # 'economía-y-finanzas-29',
    # 'gobernabilidad-24',
    ]

    @unittest.skip("Skipping test_get_datasets_by_category")
    def test_get_datasets(self):
        datasets = pe.get_datasets(Categories.MEDIO_AMBIENTE, limit=2)
        self.assertEqual(len(datasets), 2)
        self.assertIsInstance(datasets[0], Dataset)

    @unittest.skip("Skipping test_get_datasets_by_category_multiple_pages")
    def test_get_datasets_multiple_pages(self):
        datasets = pe.get_datasets(Categories.MEDIO_AMBIENTE, limit=30)
        self.assertEqual(len(datasets), 30)
        self.assertIsInstance(datasets[0], Dataset)

    #@unittest.skip("Skipping test_expand_datasets")
    #def test_expand_datasets(self):
        #datasets = pe.get_datasets(Categories.MEDIO_AMBIENTE, limit=1)
        #expanded_datasets = pe.expand_datasets(datasets)
        #print(expanded_datasets[0].__repr__(simple=True))
        #self.assertEqual(len(expanded_datasets), 1)
    
    @unittest.skip("Skipping test_get_dataset_by_url")
    def test_get_dataset_by_url(self):
        dataset = pe.get_dataset('https://www.datosabiertos.gob.pe/dataset/dataset-01-cartera-proyectos-lambayeque-activos')
        dataset.__repr__(simple=True)
        self.assertIsInstance(dataset, Dataset)

    def test_add_new_category(self):
        Categories.register_category("NEW_EDUCACION", "Educación")
        self.assertEqual(Categories.NEW_EDUCACION, "Educación")

    @unittest.skip("Skipping test_get_datasetl")
    def test_download_dataset(self):
        dataset = pe.get_dataset('https://www.datosabiertos.gob.pe/dataset/volumen-de-desembarque-mensual-de-recursos-hidrobiol%C3%B3gicos-por-puerto-y-por-especie-en-la')
        dataset_id = dataset.id
        dataset.download_files()
        
        # Check if the folder with the dataset id exists inside 'datasets' folder
        datasets_folder = os.path.join('datasets', dataset_id)
        self.assertTrue(os.path.isdir(datasets_folder), f"Folder {datasets_folder} does not exist")

    #@unittest.skip("Skipping test_get_datasetl")
    def test_download_dataset_uri_based(self):
        dataset = pe.get_dataset('consumo-de-energía-eléctrica-de-los-clientes-de-electro-puno-saa')
        dataset_id = dataset.id
        dataset.download_files()

        # Check if the folder with the dataset id exists inside 'datasets' folder
        datasets_folder = os.path.join('datasets', dataset_id)
        self.assertTrue(os.path.isdir(datasets_folder), f"Folder {datasets_folder} does not exist")
    
    @unittest.skip('')
    def test_save_datasets(self):
        datasets = pe.get_datasets(Categories.MEDIO_AMBIENTE, limit=3)
        pe.save(datasets)
        #print(expanded_datasets[0].__repr__(simple=True))
        #self.assertEqual(len(expanded_datasets), 5)

    @unittest.skip('')
    def test_load_datasets(self):
        datasets = pe.load()
        self.assertEqual(len(datasets), 2)

    #@unittest.skip('')
    def test_download_dataset_uri_based_2(self):
        dataset = pe.get_dataset('consumo-de-energía-eléctrica-de-los-clientes-de-electro-puno-saa')
        pe.save(dataset)
        self.assertIsInstance(dataset, Dataset)

    @unittest.skip('')
    def test_load_dataset(self):
        dataset = pe.load('consumo-de-energía-eléctrica-de-los-clientes-de-electro-puno-saa')
        self.assertIsInstance(dataset, Dataset)

    #@unittest.skip('')
    def test_load_dataset_data(self):
        dataset = pe.load('consumo-de-energía-eléctrica-de-los-clientes-de-electro-puno-saa')
        data = dataset.data() # search for the only .csv file or data file otherwise needs a name as argument
        self.assertIsInstance(data['Consumo de energía eléctrica de los clientes de Electro Puno S.A.A. - [Electro Puno S.A.A.] - Febrero 2023.csv'], pd.DataFrame)
    
    #@unittest.skip('')
    def test_load_dataset_data_1(self):
        datasets = pe.load()
        print(datasets[1].title)
        data = datasets[1].data('Consumo de energía eléctrica de los clientes de Electro Puno S.A.A. - [Electro Puno S.A.A.] - Enero 2023.csv') # search for the only .csv file or data file otherwise needs a name as argument
        print(data.head())

    def test_get_dataset_and_data_directly(self):
        dataset = pe.get_dataset('alumnos-matriculados-en-la-universidad-nacional-de-ingeniería-uni')
        data = dataset.data()
        print(len(data))
        print(data)


    def test_get_dataset_and_access_to_data_dictionary_directly(self):
        dataset = pe.get_dataset('alumnos-matriculados-en-la-universidad-nacional-de-ingeniería-uni')
        dic = dataset.data_dictionary
        print(dic)

    def test_load_dataset_show_files(self):
        datasets = pe.load()
        print(datasets[0].files)

    def test_search_category_1(self):
        datasets = pe.get_datasets(Categories.MODELO_DE_GESTION_DOCUMENTAL)

    def test_search_category_2(self):
        datasets = pe.get_datasets(Categories.ALIMENTACION_Y_NUTRICION, log_errors=True)

    def test_search_category_iterator(self):
        for dataset in pe.get_datasets(Categories.MODELO_DE_GESTION_DOCUMENTAL, show_progress=True, log_errors=True, as_iterator=True):
            pe.expand_dataset(dataset)
            data_dictionary = dataset.data_dictionary
            pe.save(dataset)

    def test_stats(self):
        pe.stats()

    def test_datasets_download(self):
        for category in self.categories:
            print(f"Category: {category}")
            for dataset in pe.get_datasets(category, show_progress=True, log_errors=True, as_iterator=True):
                pe.expand_dataset(dataset)
                dataset.download_files(log_errors=True, skip_existing=True)
                pe.save(dataset)

if __name__ == '__main__':
    unittest.main()