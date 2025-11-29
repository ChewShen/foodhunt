import osmnx as ox
import pandas as pd # Import pandas (osmnx requires it for GeoDataFrames)
from django.core.management.base import BaseCommand
from foodhunting.models import shopLists # Your shop model

class Command(BaseCommand):
    help = 'Fetches restaurants for Kuchai Lama area using coordinates.'

    def handle(self, *args, **kwargs):
        # 1. DEFINE VARIABLES FIRST
        center_lat = 3.089787      # Latitude of Kuchai Lama center
        center_lon = 101.686358    # Longitude of Kuchai Lama center
        distance_meters = 2000     # 
        center_point = (center_lat, center_lon)
        tags = {'amenity': 'restaurant'} # Define tags BEFORE using them

        # 2. PERFORM THE SINGLE, RELIABLE SEARCH
        self.stdout.write(f"Fetching data for {distance_meters}m around {center_point}...")
        try:
            # Use the working features_from_point method
            gdf = ox.features_from_point(center_point, dist=distance_meters, tags=tags)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"OSMnx search failed: {e}"))
            return

        # 3. SAVE THE DATA
        self.stdout.write(f"Saving {len(gdf)} shops to the database...")
        
        for index, row in gdf.iterrows():
            # Check for name and ensure geometry is a Polygon/Point (or skip)
            if 'name' in row and str(row['name']) != 'nan' and row.geometry:
                
                # Get coordinates from the geometry's centroid
                geom = row.geometry
                lat = geom.centroid.y
                lon = geom.centroid.x

                # Create or update the shop entry
                raw_cuisine = row.get('cuisine', '')
                if isinstance(raw_cuisine, list):
                    clean_cuisine = ", ".join(raw_cuisine)
                else:
                    clean_cuisine = str(raw_cuisine)
                CURRENT_AREA = 'Kuchai Lama'
                # 2. SAVE WITH HARDCODED AREA
                shopLists.objects.get_or_create(
                    name=row['name'],
                    area=CURRENT_AREA,      # <--- MOVED HERE (Part of the ID check)
                    
                    defaults={
                        'latitude': lat, 
                        'longitude': lon,
                        # 'area': ... (Removed from here)
                        'location': row.get('addr:street', ''),
                        'cuisine': clean_cuisine,
                        'phone': row.get('phone', ''),
                        'website': row.get('website', ''),
                        'opening_hours': row.get('opening_hours', ''),
                        'price': row.get('price', ''), 
                    }
                )
        self.stdout.write(self.style.SUCCESS("Data import complete!"))