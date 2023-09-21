from extract_data import Extractor
import geopandas as gpd
from geojson import FeatureCollection

extractor = Extractor()
municipios_folder = 'data/municipios/'
state_folder = 'data/estados/'

def city_routine(extract_individuals=False, extract_all=False):
    if extract_individuals:
        for state in extractor.estados:
            results = extractor.extract_geojsons(state=state)
            feature_collection = FeatureCollection(results)
            gdf_cities = gpd.GeoDataFrame.from_features(feature_collection['features'])
            gdf_cities.to_file(municipios_folder + state + '.json', driver='GeoJSON')

    if extract_all:
        results = extractor.extract_geojsons()
        feature_collection = FeatureCollection(results)
        gdf_cities = gpd.GeoDataFrame.from_features(feature_collection['features'])
        gdf_cities.to_file(municipios_folder + 'municipios.json', driver='GeoJSON')

def state_routine(extract_individuals=False, extract_all=False):
    if extract_individuals:
        for state in extractor.estados:
            results = extractor.extract_geojsons(state=state)
            feature_collection = FeatureCollection(results)
            gdf_cities = gpd.GeoDataFrame.from_features(feature_collection['features'])
            gdf_cities.to_file(state_folder + state + '.json', driver='GeoJSON')

    if extract_all:
        results = extractor.extract_geojsons()
        feature_collection = FeatureCollection(results)
        gdf_cities = gpd.GeoDataFrame.from_features(feature_collection['features'])
        gdf_cities.to_file(state_folder + 'estados.json', driver='GeoJSON')

if __name__ == '__main__':
    state_routine(extract_all=True)