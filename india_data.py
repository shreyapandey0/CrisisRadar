import json
from typing import Dict, List, Any, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IndiaData:
    def __init__(self):
        """Initialize India-specific data"""
        self.states_data = self._load_states_data()
        self.emergency_resources = self._load_emergency_resources()
        self.major_cities = self._load_major_cities()
    
    def _load_states_data(self) -> Dict[str, Any]:
        """Load Indian states and union territories data"""
        return {
            'Andhra Pradesh': {
                'capital': 'Amaravati',
                'major_cities': ['Visakhapatnam', 'Vijayawada', 'Guntur', 'Tirupati'],
                'coordinates': (15.9129, 79.7400),
                'area_km2': 160205,
                'population': 49386799,
                'common_disasters': ['cyclone', 'flood', 'drought', 'heatwave']
            },
            'Arunachal Pradesh': {
                'capital': 'Itanagar',
                'major_cities': ['Itanagar', 'Naharlagun', 'Pasighat'],
                'coordinates': (28.2180, 94.7278),
                'area_km2': 83743,
                'population': 1383727,
                'common_disasters': ['earthquake', 'landslide', 'flood']
            },
            'Assam': {
                'capital': 'Dispur',
                'major_cities': ['Guwahati', 'Silchar', 'Dibrugarh', 'Jorhat'],
                'coordinates': (26.2006, 92.9376),
                'area_km2': 78438,
                'population': 31205576,
                'common_disasters': ['flood', 'earthquake', 'erosion']
            },
            'Bihar': {
                'capital': 'Patna',
                'major_cities': ['Patna', 'Gaya', 'Bhagalpur', 'Muzaffarpur'],
                'coordinates': (25.0961, 85.3131),
                'area_km2': 94163,
                'population': 104099452,
                'common_disasters': ['flood', 'drought', 'earthquake']
            },
            'Chhattisgarh': {
                'capital': 'Raipur',
                'major_cities': ['Raipur', 'Bhilai', 'Bilaspur', 'Korba'],
                'coordinates': (21.2787, 81.8661),
                'area_km2': 135192,
                'population': 25545198,
                'common_disasters': ['drought', 'flood', 'heatwave']
            },
            'Goa': {
                'capital': 'Panaji',
                'major_cities': ['Panaji', 'Vasco da Gama', 'Margao'],
                'coordinates': (15.2993, 74.1240),
                'area_km2': 3702,
                'population': 1458545,
                'common_disasters': ['cyclone', 'flood']
            },
            'Gujarat': {
                'capital': 'Gandhinagar',
                'major_cities': ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot'],
                'coordinates': (22.2587, 71.1924),
                'area_km2': 196244,
                'population': 60439692,
                'common_disasters': ['earthquake', 'cyclone', 'drought', 'flood']
            },
            'Haryana': {
                'capital': 'Chandigarh',
                'major_cities': ['Faridabad', 'Gurgaon', 'Panipat', 'Ambala'],
                'coordinates': (29.0588, 76.0856),
                'area_km2': 44212,
                'population': 25351462,
                'common_disasters': ['flood', 'drought', 'heatwave']
            },
            'Himachal Pradesh': {
                'capital': 'Shimla',
                'major_cities': ['Shimla', 'Dharamshala', 'Solan', 'Mandi'],
                'coordinates': (31.1048, 77.1734),
                'area_km2': 55673,
                'population': 6864602,
                'common_disasters': ['earthquake', 'landslide', 'avalanche', 'flood']
            },
            'Jharkhand': {
                'capital': 'Ranchi',
                'major_cities': ['Ranchi', 'Jamshedpur', 'Dhanbad', 'Bokaro'],
                'coordinates': (23.6102, 85.2799),
                'area_km2': 79716,
                'population': 33406061,
                'common_disasters': ['drought', 'flood', 'heatwave']
            },
            'Karnataka': {
                'capital': 'Bangalore',
                'major_cities': ['Bangalore', 'Mysore', 'Hubli-Dharwad', 'Mangalore'],
                'coordinates': (15.3173, 75.7139),
                'area_km2': 191791,
                'population': 61095297,
                'common_disasters': ['drought', 'flood', 'cyclone']
            },
            'Kerala': {
                'capital': 'Thiruvananthapuram',
                'major_cities': ['Kochi', 'Thiruvananthapuram', 'Kozhikode', 'Thrissur'],
                'coordinates': (10.8505, 76.2711),
                'area_km2': 38852,
                'population': 33406061,
                'common_disasters': ['flood', 'landslide', 'cyclone']
            },
            'Madhya Pradesh': {
                'capital': 'Bhopal',
                'major_cities': ['Indore', 'Bhopal', 'Jabalpur', 'Gwalior'],
                'coordinates': (22.9734, 78.6569),
                'area_km2': 308245,
                'population': 72626809,
                'common_disasters': ['drought', 'flood', 'heatwave']
            },
            'Maharashtra': {
                'capital': 'Mumbai',
                'major_cities': ['Mumbai', 'Pune', 'Nagpur', 'Thane'],
                'coordinates': (19.7515, 75.7139),
                'area_km2': 307713,
                'population': 112374333,
                'common_disasters': ['flood', 'drought', 'cyclone', 'earthquake']
            },
            'Manipur': {
                'capital': 'Imphal',
                'major_cities': ['Imphal', 'Thoubal', 'Bishnupur'],
                'coordinates': (24.6637, 93.9063),
                'area_km2': 22327,
                'population': 2855794,
                'common_disasters': ['earthquake', 'landslide', 'flood']
            },
            'Meghalaya': {
                'capital': 'Shillong',
                'major_cities': ['Shillong', 'Tura', 'Nongstoin'],
                'coordinates': (25.4670, 91.3662),
                'area_km2': 22429,
                'population': 2966889,
                'common_disasters': ['earthquake', 'landslide', 'flood']
            },
            'Mizoram': {
                'capital': 'Aizawl',
                'major_cities': ['Aizawl', 'Lunglei', 'Saiha'],
                'coordinates': (23.1645, 92.9376),
                'area_km2': 21081,
                'population': 1097206,
                'common_disasters': ['earthquake', 'landslide', 'cyclone']
            },
            'Nagaland': {
                'capital': 'Kohima',
                'major_cities': ['Dimapur', 'Kohima', 'Mokokchung'],
                'coordinates': (26.1584, 94.5624),
                'area_km2': 16579,
                'population': 1978502,
                'common_disasters': ['earthquake', 'landslide', 'flood']
            },
            'Odisha': {
                'capital': 'Bhubaneswar',
                'major_cities': ['Bhubaneswar', 'Cuttack', 'Rourkela', 'Brahmapur'],
                'coordinates': (20.9517, 85.0985),
                'area_km2': 155707,
                'population': 42278111,
                'common_disasters': ['cyclone', 'flood', 'drought', 'heatwave']
            },
            'Punjab': {
                'capital': 'Chandigarh',
                'major_cities': ['Ludhiana', 'Amritsar', 'Jalandhar', 'Patiala'],
                'coordinates': (31.1471, 75.3412),
                'area_km2': 50362,
                'population': 27743338,
                'common_disasters': ['flood', 'drought', 'heatwave']
            },
            'Rajasthan': {
                'capital': 'Jaipur',
                'major_cities': ['Jaipur', 'Jodhpur', 'Kota', 'Bikaner'],
                'coordinates': (27.0238, 74.2179),
                'area_km2': 342239,
                'population': 68548437,
                'common_disasters': ['drought', 'flood', 'heatwave', 'dust storm']
            },
            'Sikkim': {
                'capital': 'Gangtok',
                'major_cities': ['Gangtok', 'Namchi', 'Gyalshing'],
                'coordinates': (27.5330, 88.5122),
                'area_km2': 7096,
                'population': 610577,
                'common_disasters': ['earthquake', 'landslide', 'flood']
            },
            'Tamil Nadu': {
                'capital': 'Chennai',
                'major_cities': ['Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli'],
                'coordinates': (11.1271, 78.6569),
                'area_km2': 130060,
                'population': 72147030,
                'common_disasters': ['cyclone', 'flood', 'drought', 'tsunami']
            },
            'Telangana': {
                'capital': 'Hyderabad',
                'major_cities': ['Hyderabad', 'Warangal', 'Nizamabad', 'Khammam'],
                'coordinates': (18.1124, 79.0193),
                'area_km2': 112077,
                'population': 35003674,
                'common_disasters': ['drought', 'flood', 'heatwave']
            },
            'Tripura': {
                'capital': 'Agartala',
                'major_cities': ['Agartala', 'Dharmanagar', 'Udaipur'],
                'coordinates': (23.9408, 91.9882),
                'area_km2': 10486,
                'population': 3673917,
                'common_disasters': ['flood', 'earthquake', 'landslide']
            },
            'Uttarakhand': {
                'capital': 'Dehradun',
                'major_cities': ['Dehradun', 'Haridwar', 'Roorkee', 'Nainital'],
                'coordinates': (30.0668, 79.0193),
                'area_km2': 53483,
                'population': 10086292,
                'common_disasters': ['earthquake', 'landslide', 'flood', 'avalanche']
            },
            'Uttar Pradesh': {
                'capital': 'Lucknow',
                'major_cities': ['Lucknow', 'Kanpur', 'Ghaziabad', 'Agra'],
                'coordinates': (26.8467, 80.9462),
                'area_km2': 240928,
                'population': 199812341,
                'common_disasters': ['flood', 'drought', 'earthquake', 'heatwave']
            },
            'West Bengal': {
                'capital': 'Kolkata',
                'major_cities': ['Kolkata', 'Howrah', 'Durgapur', 'Asansol'],
                'coordinates': (22.9868, 87.8550),
                'area_km2': 88752,
                'population': 91276115,
                'common_disasters': ['cyclone', 'flood', 'earthquake']
            },
            # Union Territories
            'Andaman and Nicobar Islands': {
                'capital': 'Port Blair',
                'major_cities': ['Port Blair'],
                'coordinates': (11.7401, 92.6586),
                'area_km2': 8249,
                'population': 380581,
                'common_disasters': ['tsunami', 'cyclone', 'earthquake']
            },
            'Chandigarh': {
                'capital': 'Chandigarh',
                'major_cities': ['Chandigarh'],
                'coordinates': (30.7333, 76.7794),
                'area_km2': 114,
                'population': 1055450,
                'common_disasters': ['earthquake', 'flood']
            },
            'Dadra and Nagar Haveli and Daman and Diu': {
                'capital': 'Daman',
                'major_cities': ['Daman', 'Diu', 'Silvassa'],
                'coordinates': (20.3974, 72.8328),
                'area_km2': 603,
                'population': 585764,
                'common_disasters': ['cyclone', 'flood']
            },
            'Delhi': {
                'capital': 'New Delhi',
                'major_cities': ['New Delhi', 'Delhi'],
                'coordinates': (28.6139, 77.2090),
                'area_km2': 1484,
                'population': 16787941,
                'common_disasters': ['flood', 'earthquake', 'heatwave', 'air pollution']
            },
            'Jammu and Kashmir': {
                'capital': 'Srinagar (Summer), Jammu (Winter)',
                'major_cities': ['Srinagar', 'Jammu', 'Anantnag'],
                'coordinates': (34.0837, 74.7973),
                'area_km2': 55538,
                'population': 12267032,
                'common_disasters': ['earthquake', 'avalanche', 'flood', 'landslide']
            },
            'Ladakh': {
                'capital': 'Leh',
                'major_cities': ['Leh', 'Kargil'],
                'coordinates': (34.2996, 78.2932),
                'area_km2': 59146,
                'population': 274000,
                'common_disasters': ['earthquake', 'avalanche', 'landslide']
            },
            'Lakshadweep': {
                'capital': 'Kavaratti',
                'major_cities': ['Kavaratti'],
                'coordinates': (10.5667, 72.6417),
                'area_km2': 32,
                'population': 64473,
                'common_disasters': ['cyclone', 'tsunami']
            },
            'Puducherry': {
                'capital': 'Puducherry',
                'major_cities': ['Puducherry', 'Karaikal'],
                'coordinates': (11.9416, 79.8083),
                'area_km2': 483,
                'population': 1247953,
                'common_disasters': ['cyclone', 'tsunami', 'flood']
            }
        }
    
    def _load_emergency_resources(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load emergency resources data"""
        return {
            'hospital': [
                {'name': 'AIIMS Delhi', 'location': 'Delhi', 'coordinates': (28.5672, 77.2100), 'contact': '011-26588500'},
                {'name': 'Apollo Hospital Chennai', 'location': 'Chennai', 'coordinates': (13.0674, 80.2376), 'contact': '044-28296000'},
                {'name': 'Fortis Hospital Mumbai', 'location': 'Mumbai', 'coordinates': (19.1075, 72.8263), 'contact': '022-66754444'},
                {'name': 'Manipal Hospital Bangalore', 'location': 'Bangalore', 'coordinates': (12.9057, 77.5826), 'contact': '080-25024444'},
                {'name': 'PGIMER Chandigarh', 'location': 'Chandigarh', 'coordinates': (30.7646, 76.7687), 'contact': '0172-2755555'},
                {'name': 'SGPGIMS Lucknow', 'location': 'Lucknow', 'coordinates': (26.8397, 80.9988), 'contact': '0522-2668700'},
                {'name': 'JIPMER Puducherry', 'location': 'Puducherry', 'coordinates': (11.9416, 79.8083), 'contact': '0413-2296000'},
                {'name': 'KEM Hospital Mumbai', 'location': 'Mumbai', 'coordinates': (19.0037, 72.8409), 'contact': '022-24107000'},
                {'name': 'Grant Medical College Mumbai', 'location': 'Mumbai', 'coordinates': (18.9667, 72.8263), 'contact': '022-23735555'},
                {'name': 'CMC Vellore', 'location': 'Vellore', 'coordinates': (12.9202, 79.1333), 'contact': '0416-2281000'}
            ],
            'police': [
                {'name': 'Delhi Police Headquarters', 'location': 'Delhi', 'coordinates': (28.6139, 77.2090), 'contact': '011-23490026'},
                {'name': 'Mumbai Police Headquarters', 'location': 'Mumbai', 'coordinates': (18.9388, 72.8354), 'contact': '022-22694444'},
                {'name': 'Chennai Police Headquarters', 'location': 'Chennai', 'coordinates': (13.0827, 80.2707), 'contact': '044-28447111'},
                {'name': 'Bangalore Police Headquarters', 'location': 'Bangalore', 'coordinates': (12.9716, 77.5946), 'contact': '080-22943030'},
                {'name': 'Kolkata Police Headquarters', 'location': 'Kolkata', 'coordinates': (22.5726, 88.3639), 'contact': '033-22143737'},
                {'name': 'Hyderabad Police Headquarters', 'location': 'Hyderabad', 'coordinates': (17.3850, 78.4867), 'contact': '040-27853333'},
                {'name': 'Pune Police Headquarters', 'location': 'Pune', 'coordinates': (18.5204, 73.8567), 'contact': '020-26128888'},
                {'name': 'Ahmedabad Police Headquarters', 'location': 'Ahmedabad', 'coordinates': (23.0225, 72.5714), 'contact': '079-25506789'},
                {'name': 'Jaipur Police Headquarters', 'location': 'Jaipur', 'coordinates': (26.9124, 75.7873), 'contact': '0141-2743243'},
                {'name': 'Lucknow Police Headquarters', 'location': 'Lucknow', 'coordinates': (26.8467, 80.9462), 'contact': '0522-2208888'}
            ],
            'shelter': [
                {'name': 'Red Cross Society Delhi', 'location': 'Delhi', 'coordinates': (28.6139, 77.2090), 'contact': '011-23711551'},
                {'name': 'Salvation Army Mumbai', 'location': 'Mumbai', 'coordinates': (19.0760, 72.8777), 'contact': '022-22664343'},
                {'name': 'Goonj Relief Center', 'location': 'Delhi', 'coordinates': (28.6139, 77.2090), 'contact': '011-26972986'},
                {'name': 'Akshaya Patra Foundation', 'location': 'Bangalore', 'coordinates': (12.9716, 77.5946), 'contact': '080-30143333'},
                {'name': 'Bhumi NGO', 'location': 'Chennai', 'coordinates': (13.0827, 80.2707), 'contact': '044-42018472'},
                {'name': 'CRY - Child Rights and You', 'location': 'Mumbai', 'coordinates': (19.0760, 72.8777), 'contact': '022-26663394'},
                {'name': 'Helpage India', 'location': 'Delhi', 'coordinates': (28.6139, 77.2090), 'contact': '011-41688955'},
                {'name': 'United Way Mumbai', 'location': 'Mumbai', 'coordinates': (19.0760, 72.8777), 'contact': '022-66602444'},
                {'name': 'Smile Foundation', 'location': 'Delhi', 'coordinates': (28.6139, 77.2090), 'contact': '011-43123700'},
                {'name': 'Give India Foundation', 'location': 'Bangalore', 'coordinates': (12.9716, 77.5946), 'contact': '080-67473721'}
            ],
            'fire_station': [
                {'name': 'Delhi Fire Service HQ', 'location': 'Delhi', 'coordinates': (28.6139, 77.2090), 'contact': '011-23221111'},
                {'name': 'Mumbai Fire Brigade HQ', 'location': 'Mumbai', 'coordinates': (18.9388, 72.8354), 'contact': '022-23076111'},
                {'name': 'Chennai Fire Service', 'location': 'Chennai', 'coordinates': (13.0827, 80.2707), 'contact': '044-28447500'},
                {'name': 'Bangalore Fire Department', 'location': 'Bangalore', 'coordinates': (12.9716, 77.5946), 'contact': '080-22942222'},
                {'name': 'Kolkata Fire Service', 'location': 'Kolkata', 'coordinates': (22.5726, 88.3639), 'contact': '033-22143636'},
                {'name': 'Hyderabad Fire Department', 'location': 'Hyderabad', 'coordinates': (17.3850, 78.4867), 'contact': '040-23204444'},
                {'name': 'Pune Fire Department', 'location': 'Pune', 'coordinates': (18.5204, 73.8567), 'contact': '020-26127777'},
                {'name': 'Ahmedabad Fire Department', 'location': 'Ahmedabad', 'coordinates': (23.0225, 72.5714), 'contact': '079-25506101'},
                {'name': 'Jaipur Fire Department', 'location': 'Jaipur', 'coordinates': (26.9124, 75.7873), 'contact': '0141-2743101'},
                {'name': 'Lucknow Fire Department', 'location': 'Lucknow', 'coordinates': (26.8467, 80.9462), 'contact': '0522-2208101'}
            ]
        }
    
    def _load_major_cities(self) -> List[Dict[str, Any]]:
        """Load major Indian cities data"""
        return [
            {'name': 'Mumbai', 'state': 'Maharashtra', 'coordinates': (19.0760, 72.8777), 'population': 12442373},
            {'name': 'Delhi', 'state': 'Delhi', 'coordinates': (28.6139, 77.2090), 'population': 11034555},
            {'name': 'Bangalore', 'state': 'Karnataka', 'coordinates': (12.9716, 77.5946), 'population': 8443675},
            {'name': 'Hyderabad', 'state': 'Telangana', 'coordinates': (17.3850, 78.4867), 'population': 6993262},
            {'name': 'Ahmedabad', 'state': 'Gujarat', 'coordinates': (23.0225, 72.5714), 'population': 5577940},
            {'name': 'Chennai', 'state': 'Tamil Nadu', 'coordinates': (13.0827, 80.2707), 'population': 4646732},
            {'name': 'Kolkata', 'state': 'West Bengal', 'coordinates': (22.5726, 88.3639), 'population': 4496694},
            {'name': 'Surat', 'state': 'Gujarat', 'coordinates': (21.1702, 72.8311), 'population': 4467797},
            {'name': 'Pune', 'state': 'Maharashtra', 'coordinates': (18.5204, 73.8567), 'population': 3124458},
            {'name': 'Jaipur', 'state': 'Rajasthan', 'coordinates': (26.9124, 75.7873), 'population': 3046163},
            {'name': 'Lucknow', 'state': 'Uttar Pradesh', 'coordinates': (26.8467, 80.9462), 'population': 2817105},
            {'name': 'Kanpur', 'state': 'Uttar Pradesh', 'coordinates': (26.4499, 80.3319), 'population': 2767031},
            {'name': 'Nagpur', 'state': 'Maharashtra', 'coordinates': (21.1458, 79.0882), 'population': 2405421},
            {'name': 'Indore', 'state': 'Madhya Pradesh', 'coordinates': (22.7196, 75.8577), 'population': 1964086},
            {'name': 'Thane', 'state': 'Maharashtra', 'coordinates': (19.2183, 72.9781), 'population': 1841488},
            {'name': 'Bhopal', 'state': 'Madhya Pradesh', 'coordinates': (23.2599, 77.4126), 'population': 1798218},
            {'name': 'Visakhapatnam', 'state': 'Andhra Pradesh', 'coordinates': (17.6868, 83.2185), 'population': 1730320},
            {'name': 'Pimpri-Chinchwad', 'state': 'Maharashtra', 'coordinates': (18.6298, 73.7997), 'population': 1729359},
            {'name': 'Patna', 'state': 'Bihar', 'coordinates': (25.5941, 85.1376), 'population': 1684222},
            {'name': 'Vadodara', 'state': 'Gujarat', 'coordinates': (22.3072, 73.1812), 'population': 1670806}
        ]
    
    def get_state_info(self, state_name: str) -> Dict[str, Any]:
        """Get information about a specific state"""
        return self.states_data.get(state_name, {})
    
    def get_all_states(self) -> List[str]:
        """Get list of all Indian states and union territories"""
        return list(self.states_data.keys())
    
    def get_state_by_coordinates(self, latitude: float, longitude: float) -> str:
        """Find state by coordinates (approximate)"""
        min_distance = float('inf')
        closest_state = 'Unknown'
        
        for state_name, state_data in self.states_data.items():
            state_lat, state_lon = state_data['coordinates']
            distance = ((latitude - state_lat) ** 2 + (longitude - state_lon) ** 2) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                closest_state = state_name
        
        return closest_state
    
    def get_emergency_resources(self, resource_type: str, location: str = None) -> List[Dict[str, Any]]:
        """Get emergency resources of specified type"""
        resources = self.emergency_resources.get(resource_type, [])
        
        if location:
            # Filter by location
            filtered_resources = []
            for resource in resources:
                if location.lower() in resource['location'].lower():
                    filtered_resources.append(resource)
            return filtered_resources
        
        return resources
    
    def get_state_boundaries(self) -> List[Dict[str, Any]]:
        """Get simplified state boundaries for map display"""
        # This is a simplified representation - in a real application, 
        # you would load actual GeoJSON boundary data
        boundaries = []
        
        for state_name, state_data in self.states_data.items():
            lat, lon = state_data['coordinates']
            
            # Create a simple rectangular boundary around the state center
            # In practice, you would use actual state boundary GeoJSON data
            boundary = {
                'name': state_name,
                'boundary': {
                    'type': 'Feature',
                    'properties': {'name': state_name},
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [[
                            [lon - 1, lat - 1],
                            [lon + 1, lat - 1],
                            [lon + 1, lat + 1],
                            [lon - 1, lat + 1],
                            [lon - 1, lat - 1]
                        ]]
                    }
                }
            }
            boundaries.append(boundary)
        
        return boundaries
    
    def get_disaster_prone_areas(self, disaster_type: str) -> List[str]:
        """Get areas prone to specific disaster types"""
        prone_areas = []
        
        for state_name, state_data in self.states_data.items():
            if disaster_type.lower() in state_data.get('common_disasters', []):
                prone_areas.append(state_name)
        
        return prone_areas
    
    def get_major_cities_by_state(self, state_name: str) -> List[str]:
        """Get major cities in a specific state"""
        state_data = self.states_data.get(state_name, {})
        return state_data.get('major_cities', [])
    
    def get_nearest_emergency_resources(self, latitude: float, longitude: float, 
                                      resource_type: str, radius_km: float = 50) -> List[Dict[str, Any]]:
        """Get nearest emergency resources within specified radius"""
        resources = self.emergency_resources.get(resource_type, [])
        nearby_resources = []
        
        for resource in resources:
            res_lat, res_lon = resource['coordinates']
            
            # Calculate distance using Haversine formula (simplified)
            distance = ((latitude - res_lat) ** 2 + (longitude - res_lon) ** 2) ** 0.5 * 111  # Rough km conversion
            
            if distance <= radius_km:
                resource_copy = resource.copy()
                resource_copy['distance_km'] = round(distance, 2)
                nearby_resources.append(resource_copy)
        
        # Sort by distance
        nearby_resources.sort(key=lambda x: x['distance_km'])
        
        return nearby_resources
    
    def get_population_density(self, state_name: str) -> float:
        """Get population density for a state"""
        state_data = self.states_data.get(state_name, {})
        if 'population' in state_data and 'area_km2' in state_data:
            return round(state_data['population'] / state_data['area_km2'], 2)
        return 0.0
    
    def get_crisis_statistics(self, time_period: str = 'all') -> Dict[str, Any]:
        """Get crisis statistics for India"""
        # This would normally fetch from a database
        # For now, return sample statistics
        return {
            'total_states_monitored': len(self.states_data),
            'total_cities_monitored': len(self.major_cities),
            'emergency_resources': {
                'hospitals': len(self.emergency_resources['hospital']),
                'police_stations': len(self.emergency_resources['police']),
                'fire_stations': len(self.emergency_resources['fire_station']),
                'shelters': len(self.emergency_resources['shelter'])
            },
            'disaster_prone_regions': {
                'cyclone_prone': len(self.get_disaster_prone_areas('cyclone')),
                'flood_prone': len(self.get_disaster_prone_areas('flood')),
                'earthquake_prone': len(self.get_disaster_prone_areas('earthquake')),
                'drought_prone': len(self.get_disaster_prone_areas('drought'))
            }
        }
