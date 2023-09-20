from extract_data import Extractor
import geopandas as gpd
from geojson import FeatureCollection

extractor = Extractor()

for state in extractor.estados:
    results = extractor.extract_geojsons(state=state)
    feature_collection = FeatureCollection(results)
    gdf_cities = gpd.GeoDataFrame.from_features(feature_collection['features'])
    gdf_cities.to_file('data/geojson/' + state + '.json', driver='GeoJSON')

results = extractor.extract_geojsons()
feature_collection = FeatureCollection(results)
gdf_cities = gpd.GeoDataFrame.from_features(feature_collection['features'])
gdf_cities.to_file('data/geojson/municipios.json', driver='GeoJSON')