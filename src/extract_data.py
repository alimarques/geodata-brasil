import ssl
import requests
import multiprocessing

from params import URL_MUNICIPIOS, URL_MALHAS, PROCESSORS

class TLSAdapter(requests.adapters.HTTPAdapter):
    """
        Classe para mitigar erros de SSL cmo requests
    """
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers("DEFAULT@SECLEVEL=1")
        ctx.options |= 0x4
        kwargs["ssl_context"] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)

class Extractor:
    """
        Classe Extractor extrai listagem de cidades, assim como a malha geografica de cada uma
    """
    def __init__(self):
        self.extract_cities()
        self.filter_json()

    def extract_cities(self):
        """
            Extrai as cidades da API do IBGE
        """
        with requests.session() as s:
            s.mount("https://", TLSAdapter())
            response = s.get(URL_MUNICIPIOS).json()
        self.data = response
    
    def filter_json(self):
        """
            Selecionar apenas id (codigo do IBGE), nome da cidade e Estado
        """
        self.data = [
            {
                'id':result['id'],
                'nome':result['nome'],
                'estado':result['microrregiao']['mesorregiao']['UF']['nome']
            } for result in self.data
        ]
    
    def extract_geojson(self, city):
        """
            Extrai a malha de um municipio expecifico em formato GEOJSON
        """
        id = city['id']
        url = f'{URL_MALHAS}{id}?formato=application/vnd.geo+json'
        with requests.session() as s:
            s.mount("https://", TLSAdapter())
            response = s.get(url).json()
            response['features'][0]['properties']['cidade'] = city['nome']
            response['features'][0]['properties']['estado'] = city['estado']
            features = response['features'][0]
        return features

    def extract_geojsons(self, state='all'):
        """
            Extrai a malha de todos os municipios em formato GEOJSON
            Parametros:
                - state: Estado para realizar a extracao
                    - all (default): Todos os municipios brasileiros
                    - Caso contrário, ira extrair todos os municipios de um determinado Estado brasileiro (especificar o nome)
        """
        if state == 'all':
            data_to_extract = self.data
        else:
            try:
                data_to_extract = [city for city in self.data if city['estado'] == state]
            except:
                raise ValueError("Estado não encontrado. Verifique se informou o nome corretamente.")

        # Use multiprocessing to process combinations in parallel
        with multiprocessing.Pool(processes=PROCESSORS) as pool:
            results = [city for city in pool.map(self.extract_geojson, data_to_extract)]
        self.data_geojson = results