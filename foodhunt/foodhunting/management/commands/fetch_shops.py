import osmnx as ox
from django.core.management.base import BaseCommand
from foodhunting.models import shopLists # Ensure this matches your model name

class Command(BaseCommand):
    help = 'Fetches restaurants for SS15, Mid Valley, and Cyberjaya'

    def handle(self, *args, **kwargs):
        # 1. CONFIGURATION: Exact coordinates for your target areas
        TARGET_AREAS = [
            {
                'name': 'ss15',
                'lat': 3.0751,
                'lon': 101.5891,
                'radius': 1000  # SS15 is dense, 1km covers it all
            },
            {
                'name': 'mid_valley',
                'lat': 3.1176,
                'lon': 101.6776,
                'radius': 1500  # Covers Megamall + Gardens + Northpoint
            },
            {
                'name': 'cyberjaya',
                'lat': 2.921300, 
                'lon': 101.655900,
                'radius': 3000  # Cyberjaya is wide, need 3km
            }
        ]

        tags = {'amenity': 'restaurant'}

        # 2. THE AUTOMATED LOOP
        for area_config in TARGET_AREAS:
            area_name = area_config['name']
            center_point = (area_config['lat'], area_config['lon'])
            
            self.stdout.write(f"--- Processing {area_name} ---")
            
            try:
                gdf = ox.features_from_point(center_point, dist=area_config['radius'], tags=tags)
            except Exception as e:
                self.stderr.write(f"Skipping {area_name}: {e}")
                continue

            # 3. SAVE DATA
            count = 0
            for index, row in gdf.iterrows():
                # Safety check for valid data
                if 'name' in row and str(row['name']) != 'nan' and row.geometry:
                    
                    # Get Lat/Lon
                    geom = row.geometry
                    lat = geom.centroid.y
                    lon = geom.centroid.x

                    # Clean Cuisine String
                    raw_cuisine = row.get('cuisine', '')
                    if isinstance(raw_cuisine, list):
                        clean_cuisine = ", ".join(raw_cuisine)
                    else:
                        clean_cuisine = str(raw_cuisine)

                    # Save to DB
                    shopLists.objects.get_or_create(
                        name=row['name'],
                        area=area_name, # <--- Tags it as 'ss15', 'mid_valley', etc.
                        defaults={
                            'latitude': lat, 
                            'longitude': lon,
                            'location': row.get('addr:street', ''),
                            'cuisine': clean_cuisine,
                            'phone': row.get('phone', ''),
                            'website': row.get('website', ''),
                            'opening_hours': row.get('opening_hours', ''),
                            'price': row.get('price', ''), 
                        }
                    )
                    count += 1
            
            self.stdout.write(self.style.SUCCESS(f"Saved {count} shops for {area_name}"))

        self.stdout.write(self.style.SUCCESS("All areas processed!"))