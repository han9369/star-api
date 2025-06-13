import math
from datetime import datetime
import pytz
from flatlib import const
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart


def calculate_lunar_phase(date_str):
    """
    Calculate detailed lunar phase information for a given date
    Returns: Dictionary with comprehensive lunar data
    """
    try:
        # Parse the date
        date = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Calculate lunar phase (simplified calculation)
        # This is a basic approximation - in production you'd use a more accurate algorithm
        
        # Known new moon date as reference (2024-01-11)
        known_new_moon = datetime(2024, 1, 11)
        lunar_cycle = 29.53  # Average lunar cycle in days
        
        # Calculate days since known new moon
        days_since = (date - known_new_moon).days
        
        # Calculate current phase position (0-1)
        phase_position = (days_since % lunar_cycle) / lunar_cycle
        
        # Calculate illumination percentage
        illumination = round(abs(0.5 - phase_position) * 200, 1)
        if phase_position > 0.5:
            illumination = 100 - illumination
        
        # Determine phase name and detailed info
        if phase_position < 0.0625:
            phase_name = "New Moon"
            phase_description = "The moon is hidden from view, creating optimal conditions for new beginnings and setting intentions. This is a powerful time for manifestation and planting seeds for future growth."
            energy_type = "Renewal & New Beginnings"
        elif phase_position < 0.1875:
            phase_name = "Waxing Crescent"
            phase_description = "A thin sliver of light appears, symbolizing emerging opportunities and growing momentum. This phase supports taking initial action on recent decisions and building upon new foundations."
            energy_type = "Growth & Momentum"
        elif phase_position < 0.3125:
            phase_name = "First Quarter"
            phase_description = "Half the moon is illuminated, representing a time of decision-making and overcoming obstacles. This phase brings clarity about what needs to be released or adjusted in your path forward."
            energy_type = "Decision & Action"
        elif phase_position < 0.4375:
            phase_name = "Waxing Gibbous"
            phase_description = "The moon grows fuller, enhancing intuition and bringing projects to completion. This is an excellent time for refinement, patience, and trusting the process of natural development."
            energy_type = "Refinement & Patience"
        elif phase_position < 0.5625:
            phase_name = "Full Moon"
            phase_description = "The moon shines at maximum brightness, illuminating truths and bringing situations to culmination. Emotions and psychic abilities are heightened, making this ideal for celebration and gratitude."
            energy_type = "Culmination & Revelation"
        elif phase_position < 0.6875:
            phase_name = "Waning Gibbous"
            phase_description = "The moon begins to decrease, encouraging sharing wisdom and expressing gratitude for recent achievements. This phase supports teaching others and integrating lessons learned."
            energy_type = "Gratitude & Sharing"
        elif phase_position < 0.8125:
            phase_name = "Last Quarter"
            phase_description = "Half the moon remains visible, signaling time for release and forgiveness. This phase helps clear away what no longer serves and creates space for future opportunities."
            energy_type = "Release & Forgiveness"
        else:
            phase_name = "Waning Crescent"
            phase_description = "The final sliver of moon encourages rest, reflection, and spiritual connection. This is a time for contemplation, healing, and preparing for the next cycle of growth."
            energy_type = "Rest & Reflection"
        
        # Calculate days until next major phase
        days_in_cycle = days_since % lunar_cycle
        if days_in_cycle < 7.4:
            days_to_next = 7.4 - days_in_cycle
            next_phase = "First Quarter"
        elif days_in_cycle < 14.8:
            days_to_next = 14.8 - days_in_cycle
            next_phase = "Full Moon"
        elif days_in_cycle < 22.1:
            days_to_next = 22.1 - days_in_cycle
            next_phase = "Last Quarter"
        else:
            days_to_next = 29.53 - days_in_cycle
            next_phase = "New Moon"
        
        return {
            'phase_name': phase_name,
            'illumination_percent': illumination,
            'phase_description': phase_description,
            'energy_type': energy_type,
            'days_to_next_phase': round(days_to_next, 1),
            'next_phase': next_phase,
            'lunar_day': int(days_in_cycle) + 1
        }
            
    except Exception as e:
        print(f"Error calculating lunar phase: {e}")
        return {
            'phase_name': "Unknown",
            'illumination_percent': 0,
            'phase_description': "Unable to calculate lunar phase information",
            'energy_type': "Unknown",
            'days_to_next_phase': 0,
            'next_phase': "Unknown",
            'lunar_day': 0
        }


def get_current_transits(date_str, timezone='UTC'):
    """
    Get current planetary positions for the given date
    """
    try:
        # Convert date format for flatlib
        date_formatted = date_str.replace('-', '/')
        
        # Use noon UTC for consistency
        date_obj = Datetime(date_formatted, '12:00:00', '+00:00')
        pos = GeoPos(0, 0)  # Use equator for general transits
        
        # Create chart for transits
        chart = Chart(date_obj, pos, IDs=const.LIST_OBJECTS)
        
        return chart
        
    except Exception as e:
        print(f"Error getting transits: {e}")
        return None


def get_timezone_from_longitude(longitude):
    """
    Estimate timezone from longitude
    """
    # Simple timezone estimation: longitude / 15 = hours from UTC
    timezone_offset = longitude / 15.0
    
    # Round to nearest 0.5 hour
    timezone_offset = round(timezone_offset * 2) / 2
    
    return timezone_offset


def format_timezone_offset(offset):
    """
    Format timezone offset as +HH:MM or -HH:MM
    """
    sign = '+' if offset >= 0 else '-'
    hours = int(abs(offset))
    minutes = int((abs(offset) - hours) * 60)
    
    return f"{sign}{hours:02d}:{minutes:02d}"


def get_lucky_elements(sun_sign, chart, date):
    """
    Calculate lucky elements based on astrological factors
    This is a simplified version - in production you'd use more complex calculations
    """
    
    # Lucky numbers based on planetary positions
    sun = chart.get(const.SUN)
    moon = chart.get(const.MOON)
    venus = chart.get(const.VENUS)
    
    lucky_numbers = []
    if sun:
        lucky_numbers.append(int(sun.lon / 30) + 1)  # 1-12
    if moon:
        lucky_numbers.append(int(moon.lon / 12) + 1)  # 1-30
    if venus:
        lucky_numbers.append(int(venus.lon / 40) + 1)  # 1-9
    
    # Lucky colors based on sign and planetary influences
    color_map = {
        'Aries': ['Red', 'Orange'],
        'Taurus': ['Green', 'Pink'],
        'Gemini': ['Yellow', 'Silver'],
        'Cancer': ['Silver', 'Blue'],
        'Leo': ['Gold', 'Orange'],
        'Virgo': ['Navy', 'Grey'],
        'Libra': ['Pink', 'Light Blue'],
        'Scorpio': ['Maroon', 'Black'],
        'Sagittarius': ['Purple', 'Turquoise'],
        'Capricorn': ['Brown', 'Black'],
        'Aquarius': ['Blue', 'Silver'],
        'Pisces': ['Sea Green', 'Lavender']
    }
    
    lucky_colors = color_map.get(sun_sign, ['White', 'Silver'])
    
    # Lucky direction based on Mars position
    mars = chart.get(const.MARS)
    directions = ['North', 'Northeast', 'East', 'Southeast', 'South', 'Southwest', 'West', 'Northwest']
    if mars:
        direction_index = int(mars.lon / 45) % len(directions)
        lucky_direction = directions[direction_index]
    else:
        lucky_direction = 'East'  # Default
    
    # Lucky stone based on Moon position
    stones = ['Amethyst', 'Rose Quartz', 'Citrine', 'Clear Quartz', 'Moonstone', 
              'Labradorite', 'Tiger\'s Eye', 'Aventurine', 'Carnelian', 'Sodalite']
    if moon:
        stone_index = int(moon.lon / 36) % len(stones)
        lucky_stone = stones[stone_index]
    else:
        lucky_stone = 'Clear Quartz'  # Default
    
    return {
        'numbers': sorted(lucky_numbers)[:3],  # Top 3 numbers
        'colors': lucky_colors,
        'direction': lucky_direction,
        'stone': lucky_stone
    }


def calculate_planetary_strength(planet, sign=None):
    """
    Calculate planetary strength based on dignity and other factors
    """
    base_strength = 1.0
    
    # Planetary dignities (simplified)
    dignities = {
        const.SUN: {'Leo': 2.0, 'Aries': 1.5, 'Aquarius': 0.5, 'Libra': 0.5},
        const.MOON: {'Cancer': 2.0, 'Taurus': 1.5, 'Scorpio': 0.5, 'Capricorn': 0.5},
        const.MERCURY: {'Gemini': 2.0, 'Virgo': 2.0, 'Sagittarius': 0.5, 'Pisces': 0.5},
        const.VENUS: {'Taurus': 2.0, 'Libra': 2.0, 'Scorpio': 0.5, 'Aries': 0.5},
        const.MARS: {'Aries': 2.0, 'Scorpio': 2.0, 'Libra': 0.5, 'Taurus': 0.5},
        const.JUPITER: {'Sagittarius': 2.0, 'Pisces': 2.0, 'Gemini': 0.5, 'Virgo': 0.5},
        const.SATURN: {'Capricorn': 2.0, 'Aquarius': 2.0, 'Cancer': 0.5, 'Leo': 0.5}
    }
    
    planet_id = getattr(planet, 'id', None)
    planet_sign = sign or getattr(planet, 'sign', None)
    
    if planet_id and planet_sign:
        dignity_multiplier = dignities.get(planet_id, {}).get(planet_sign, 1.0)
        return base_strength * dignity_multiplier
    
    return base_strength


def get_aspect_strength(aspect_type, orb):
    """
    Calculate aspect strength based on type and orb
    """
    # Major aspects with their base strengths
    aspect_strengths = {
        0: 2.0,    # Conjunction
        60: 1.2,   # Sextile
        90: 1.8,   # Square
        120: 1.5,  # Trine
        180: 2.0   # Opposition
    }
    
    base_strength = aspect_strengths.get(aspect_type, 0.5)
    
    # Reduce strength based on orb (larger orb = weaker aspect)
    orb_factor = max(0.1, 1.0 - (abs(orb) / 10.0))
    
    return base_strength * orb_factor


def determine_fortune_level(score):
    """
    Convert numeric score to descriptive fortune level
    """
    if score >= 8.5:
        return "Exceptionally Favorable"
    elif score >= 7.0:
        return "Very Favorable"
    elif score >= 5.5:
        return "Moderately Favorable"
    elif score >= 4.0:
        return "Balanced"
    else:
        return "Challenging"


def get_planetary_hour(date_time, latitude, longitude):
    """
    Calculate planetary hour for given time and location
    This is a simplified version - actual calculation is more complex
    """
    
    # Planetary hour sequence (starting from sunrise)
    planetary_sequence = [
        const.SUN, const.VENUS, const.MERCURY, const.MOON,
        const.SATURN, const.JUPITER, const.MARS
    ]
    
    # This is a simplified calculation
    # In reality, you'd need to calculate sunrise/sunset times
    # and divide daylight/night into 12 planetary hours each
    
    hour = date_time.hour
    day_of_week = date_time.weekday()  # 0 = Monday
    
    # Simplified planetary hour calculation
    planetary_hour_index = (day_of_week * 24 + hour) % 7
    
    return planetary_sequence[planetary_hour_index] 