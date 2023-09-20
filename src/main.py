from extract_data import Extractor
import geopandas as gpd
from geojson import FeatureCollection

extractor = Extractor()
data = extractor.extract_geojsons(state='São Paulo')

feature_collection = FeatureCollection(data)
gdf_cities = gpd.GeoDataFrame.from_features(feature_collection['features'])
gdf_cities.plot()