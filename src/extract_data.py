import ssl
import requests
import multiprocessing

from params import URL_MUNICIPIOS, URL_MALHAS_MUNICIPIOS, URL_MALHAS_ESTADOS, PROCESSORS

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
        self.extract_states_names()

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
                'estado':result['microrregiao']['mesorregiao']['UF']['nome'],
                'estado_sigla':result['microrregiao']['mesorregiao']['UF']['sigla']
            } for result in self.data
        ]
    
    def extract_states_names(self):
        """
            Extrair sigla dos Estados brasileiros
        """
        self.estados = set([city['estado_sigla'] for city in self.data])
    
    def extract_geojson_city(self, city):
        """
            Extrai a malha de um municipio expecifico em formato GeoJSON
        """
        id = city['id']
        url = f'{URL_MALHAS_MUNICIPIOS}{id}?formato=application/vnd.geo+json'
        with requests.session() as s:
            s.mount("https://", TLSAdapter())
            response = s.get(url).json()
            response['features'][0]['properties']['cidade'] = city['nome']
            response['features'][0]['properties']['estado'] = city['estado']
            features = response['features'][0]
        return features

    def extract_geojson_state(self, state):
        """
            Extrai a malha de um Estado expecifico em formato GeoJSON
            Parametros:
                - state: Sigla do Estado
        """
        url = f'{URL_MALHAS_ESTADOS}{state}?formato=application/vnd.geo+json'
        with requests.session() as s:
            s.mount("https://", TLSAdapter())
            response = s.get(url).json()
            response['features'][0]['properties']['estado_sigla'] = state
            features = response['features'][0]
        return features

    def extract_geojsons(self, state='all', type='municipios'):
        """
            Extrai a malha de todos os municipios em formato GeoJSON
            Parametros:
                - state: Estado para realizar a extracao
                    - all (default): Todos os municipios brasileiros
                    - Caso contrário, ira extrair todos os municipios de um determinado Estado brasileiro (especificar a sigla)
                - type: Tipo de extracao
                    - municipios
                    - estados
        """
        if type == 'municipios':
            if state == 'all':
                data_to_extract = self.data
            else:
                try:
                    data_to_extract = [city for city in self.data if city['estado_sigla'] == state]
                except:
                    raise ValueError("Estado não encontrado. Verifique se informou a sigla corretamente.")
        elif type == 'estados':
            data_to_extract = self.estados
        else:
            raise ValueError("Escolha entre municipios ou Estados.")

        # Use multiprocessing to process combinations in parallel
        if type == 'municipios':
            with multiprocessing.Pool(processes=PROCESSORS) as pool:
                results = [result for result in pool.map(self.extract_geojson_city, data_to_extract)]
            return results
        if type == 'estados':
            with multiprocessing.Pool(processes=PROCESSORS) as pool:
                results = [result for result in pool.map(self.extract_geojson_state, data_to_extract)]
            return results