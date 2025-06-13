import json
import random
from datetime import datetime, timedelta
from flatlib import const
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import aspects
from .utils import get_timezone_from_longitude, get_lucky_elements, get_current_transits, calculate_lunar_phase
import pytz
import random


class DailyFortuneCalculator:
    """
    Daily Fortune Calculator for Astrology
    Calculates daily horoscope based on astrological transits and user's birth chart
    """
    
    def __init__(self):
        self.wisdom_templates = [
            "Creativity is intelligence having fun. Today, let your brilliance play freely in all that you do.",
            "The universe conspires to help those who dare to dream. Your aspirations are closer than they appear.",
            "Trust your intuition today - it's your inner compass guiding you toward your highest good.",
            "Every challenge is an opportunity in disguise. Look for the gift within today's experiences.",
            "Your authentic self is your greatest strength. Shine your light without hesitation.",
        ]
        
        self.lucky_colors = [
            ['Purple', 'Emerald Green'], ['Rose Gold', 'Forest Green'], ['Silver', 'Sky Blue'],
            ['Golden Yellow', 'Royal Blue'], ['Crimson Red', 'Gold'], ['Navy Blue', 'Ivory']
        ]
        
        self.lucky_stones = ['Amethyst', 'Rose Quartz', 'Citrine', 'Clear Quartz', 'Moonstone']
        self.directions = ['North', 'Northeast', 'East', 'Southeast', 'South', 'Southwest', 'West', 'Northwest']
    
    def calculate_daily_fortune(self, birth_date, birth_time, birth_lat, birth_lon, 
                              target_date=None, target_timezone='UTC'):
        """
        Calculate daily fortune for a specific date
        
        Args:
            birth_date: Birth date in YYYY-MM-DD format
            birth_time: Birth time in HH:MM:SS format
            birth_lat: Birth latitude
            birth_lon: Birth longitude
            target_date: Target date for fortune calculation (default: today)
            target_timezone: Timezone for target date (default: UTC)
        
        Returns:
            Dictionary containing all fortune data
        """
        try:
            # Use today if no target date provided
            if target_date is None:
                target_date = datetime.now(pytz.UTC).strftime('%Y-%m-%d')
            
            # Calculate birth chart
            birth_chart = self._calculate_birth_chart(birth_date, birth_time, birth_lat, birth_lon)
            
            # Calculate current transits for target date
            transits = self._calculate_transits(target_date, target_timezone)
            
            # Calculate lunar phase
            lunar_phase_info = calculate_lunar_phase(target_date)
            
            # Calculate fortune score
            fortune_score = self._calculate_fortune_score(birth_chart, transits, lunar_phase_info['phase_name'])
            
            # Generate fortune summary
            fortune_summary = self._generate_fortune_summary(birth_chart, transits, fortune_score)
            
            # Generate wisdom for today
            wisdom = self._generate_wisdom()
            
            # Calculate lucky elements
            lucky_elements = self._calculate_lucky_elements(birth_chart, transits)
            
            # Calculate life area forecasts
            life_areas = self._calculate_life_areas(birth_chart, transits)
            
            # Generate daily guidance
            daily_guidance = self._generate_daily_guidance(birth_chart, transits, fortune_score)
            
            # Compile all results in flat structure
            result = {
                'success': True,
                'date': target_date,
                
                # Fortune Overview
                'fortune_score': fortune_score,
                'fortune_level': fortune_summary['level'],
                'fortune_summary': fortune_summary['description'],
                'wisdom_for_today': wisdom,
                
                # Lucky Elements
                'lucky_numbers': lucky_elements['lucky_numbers'],
                'lucky_colors': lucky_elements['lucky_colors'], 
                'lucky_direction': lucky_elements['lucky_direction'],
                'lucky_stone': lucky_elements['lucky_stone'],
                
                # Career & Finance
                'career_rating': life_areas['career_finance']['rating'],
                'career_forecast': life_areas['career_finance']['forecast'],
                'career_tip': life_areas['career_finance']['tip'],
                
                # Love & Relationships
                'love_rating': life_areas['love_relationships']['rating'],
                'love_forecast': life_areas['love_relationships']['forecast'],
                'love_tip': life_areas['love_relationships']['tip'],
                
                # Health & Wellness
                'health_rating': life_areas['health_wellness']['rating'],
                'health_forecast': life_areas['health_wellness']['forecast'],
                'health_tip': life_areas['health_wellness']['tip'],
                
                # Personal Growth
                'growth_rating': life_areas['personal_growth']['rating'],
                'growth_forecast': life_areas['personal_growth']['forecast'],
                'growth_tip': life_areas['personal_growth']['tip'],
                
                # Daily Guidance
                'focus_today': daily_guidance['focus_of_the_day'],
                'challenges_today': daily_guidance['challenges_to_navigate'],
                
                # Lunar Phase Information
                'lunar_phase_name': lunar_phase_info['phase_name'],
                'lunar_illumination_percent': lunar_phase_info['illumination_percent'],
                'lunar_energy_type': lunar_phase_info['energy_type'],
                'days_to_next_lunar_phase': lunar_phase_info['days_to_next_phase'],
                'lunar_phase_description': lunar_phase_info['phase_description'],
                
                # Additional Information
                'auspicious_hours': self._calculate_auspicious_hours(transits)
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_birth_chart(self, date, time, lat, lon):
        """Calculate birth chart"""
        try:
            # Convert date format for flatlib
            date_str = date.replace('-', '/')
            
            # Estimate timezone from longitude
            timezone_offset = lon / 15.0
            timezone_offset = round(timezone_offset * 2) / 2
            
            # Format timezone
            hours = int(timezone_offset)
            minutes = int(abs(timezone_offset - hours) * 60)
            sign = '+' if timezone_offset >= 0 else '-'
            utc_offset = f"{sign}{abs(hours):02d}:{abs(minutes):02d}"
            
            # Create datetime object
            date_obj = Datetime(date_str, time, utc_offset)
            pos = GeoPos(lat, lon)
            
            # Create chart
            chart = Chart(date_obj, pos, IDs=const.LIST_OBJECTS)
            return chart
            
        except Exception as e:
            raise Exception(f"Birth chart calculation error: {str(e)}")
    
    def _calculate_transits(self, date, timezone='UTC'):
        """Calculate current planetary transits"""
        try:
            # Convert date format
            date_str = date.replace('-', '/')
            
            # Use noon UTC for transit calculations
            date_obj = Datetime(date_str, '12:00:00', '+00:00')
            pos = GeoPos(0, 0)  # Use equator for general transits
            
            # Create transit chart
            transit_chart = Chart(date_obj, pos, IDs=const.LIST_OBJECTS)
            return transit_chart
            
        except Exception as e:
            raise Exception(f"Transit calculation error: {str(e)}")
    
    def _calculate_auspicious_hours(self, transits):
        """Calculate auspicious hours for the day"""
        # Simplified calculation based on planetary hours
        # In a real implementation, this would be more sophisticated
        
        auspicious_periods = []
        
        # Morning meditation period (based on Jupiter influence)
        jupiter = transits.get(const.JUPITER)
        if jupiter:
            auspicious_periods.append({
                'time_range': '7:00-9:00',
                'activity': 'Meditation & Planning'
            })
        
        # Business meeting period (based on Mercury influence)
        mercury = transits.get(const.MERCURY)
        if mercury:
            auspicious_periods.append({
                'time_range': '13:00-15:00',
                'activity': 'Business Meetings'
            })
        
        return auspicious_periods
    
    def _calculate_fortune_score(self, birth_chart, transits, lunar_phase):
        """Calculate overall fortune score (1-100 integer scale)"""
        base_score = 50  # Start from middle point
        
        # Analyze major planetary influences
        sun_influence = self._analyze_planet_influence(birth_chart, transits, const.SUN)
        moon_influence = self._analyze_planet_influence(birth_chart, transits, const.MOON)
        venus_influence = self._analyze_planet_influence(birth_chart, transits, const.VENUS)
        jupiter_influence = self._analyze_planet_influence(birth_chart, transits, const.JUPITER)
        
        # Weight the influences (scale to +/- 40 points)
        total_influence = (sun_influence * 12 + moon_influence * 10 + 
                          venus_influence * 8 + jupiter_influence * 10)
        
        # Lunar phase bonus (scale to +/- 10 points)
        lunar_bonus = self._get_lunar_phase_bonus(lunar_phase) * 15
        
        # Calculate final score
        final_score = base_score + total_influence + lunar_bonus
        
        # Ensure score is within 1-100 range and return as integer
        return int(max(1, min(100, final_score)))
    
    def _generate_fortune_summary(self, birth_chart, transits, fortune_score):
        """Generate detailed fortune summary"""
        sun_sign = birth_chart.get(const.SUN).sign
        
        # Get base description and expand it
        if fortune_score >= 85:
            level = "Exceptionally Favorable"
            descriptions = [
                "Today's celestial alignment creates an extraordinary environment for creative thinking and meaningful connections. Your communication skills are heightened to remarkable levels, making this an ideal day for important conversations, presentations, and negotiations. The planetary energies are flowing in perfect harmony with your natural tendencies, opening doors that may have seemed closed before. This is one of those rare days when the universe seems to conspire in your favor, so trust your instincts and take bold action.",
                
                "The stars have aligned in a particularly auspicious configuration today, bringing forth opportunities that could have lasting positive impact on your life. Your intuitive abilities are exceptionally sharp, allowing you to read between the lines in both personal and professional situations. The cosmic energy supports ambitious endeavors and creative projects, while also enhancing your magnetic appeal to others. Consider this a green light from the universe to pursue what truly matters to you.",
                
                "Today marks a powerful convergence of beneficial planetary influences that create an atmosphere ripe for success and fulfillment. Your natural charisma is amplified, drawing positive attention and support from influential people in your sphere. The celestial mechanics are working overtime to bring synchronicities and meaningful coincidences into your path. This is an exceptional day to launch new ventures, express your authentic self, and embrace opportunities that align with your highest aspirations."
            ]
        elif fortune_score >= 70:
            level = "Very Favorable" 
            descriptions = [
                "The planetary influences are working in your favor today, creating a supportive backdrop for pursuing your goals with confidence and clarity. Your natural talents shine more brightly than usual, attracting the right kind of attention from people who can help advance your interests. The cosmic currents are flowing smoothly, reducing friction in your daily interactions and making collaboration feel effortless. This is an excellent time to build bridges, strengthen relationships, and make progress on important projects.",
                
                "Today brings a harmonious blend of cosmic energies that support both personal growth and professional advancement. Your ability to see the bigger picture is enhanced, helping you make decisions that will benefit you in the long run. The universe is offering gentle nudges in the right direction, so pay attention to subtle signs and synchronicities. Your emotional intelligence is particularly strong today, making it easier to navigate complex social dynamics and forge meaningful connections.",
                
                "The celestial atmosphere today is charged with positive potential, creating favorable conditions for manifestation and achievement. Your creative faculties are operating at a higher frequency, allowing innovative solutions to emerge naturally. The planetary aspects support confident self-expression and authentic communication, making others more receptive to your ideas and proposals. This is a day when patience and persistence will yield tangible rewards."
            ]
        elif fortune_score >= 55:
            level = "Moderately Favorable"
            descriptions = [
                "Today presents a balanced cosmic landscape that supports both reflection and purposeful action. The planetary energies are neither pushing nor pulling too strongly in any direction, giving you the freedom to choose your own pace and priorities. This steady influence creates ideal conditions for making thoughtful decisions and building solid foundations for future success. Trust your instincts while remaining open to new perspectives and unexpected opportunities that may arise.",
                
                "The celestial influences today create a stable platform for steady progress toward your goals. While there may not be dramatic breakthroughs, the consistent energy flow supports sustainable growth and meaningful connections. Your ability to balance different aspects of your life is enhanced, helping you maintain harmony between personal desires and professional responsibilities. This is a good day for consolidating recent gains and planning your next strategic moves.",
                
                "Today's astrological climate offers a measured blend of challenge and opportunity that encourages personal development. The planetary aspects create just enough tension to keep you engaged and motivated, while providing sufficient support to ensure your efforts bear fruit. Your diplomatic skills are heightened, making this an excellent time for negotiations, conflict resolution, and collaborative problem-solving. The key to maximizing today's potential lies in maintaining flexibility while staying true to your core values."
            ]
        else:
            level = "Challenging"
            descriptions = [
                "While today may present some obstacles and resistance, these challenges offer valuable opportunities for growth, resilience-building, and character development. The planetary tensions are designed to test your resolve and help you discover inner strengths you may not have known you possessed. Approach situations with patience, wisdom, and a willingness to learn from setbacks. Sometimes the universe presents difficulties as a way of redirecting us toward better paths and more authentic expressions of our true selves.",
                
                "Today's cosmic climate requires extra mindfulness and strategic thinking as you navigate through potentially turbulent waters. The planetary influences may create friction in your usual routines, pushing you to find creative solutions and alternative approaches. While this energy can feel uncomfortable, it often leads to breakthrough moments and innovative problem-solving. Focus on maintaining your center and responding rather than reacting to challenging circumstances.",
                
                "The astrological aspects today are calling for patience, adaptability, and emotional intelligence as you work through various complexities. These cosmic challenges are not punishments but rather opportunities for spiritual and personal evolution. The universe may be asking you to release outdated patterns and embrace new ways of being that better serve your highest good. Trust that current difficulties are temporary and are ultimately guiding you toward greater authenticity and fulfillment."
            ]
        
        # Randomly select one description to avoid repetition
        description = random.choice(descriptions)
        
        return {
            'level': level,
            'description': description
        }
    
    def _generate_wisdom(self):
        """Generate wisdom for today"""
        return random.choice(self.wisdom_templates)
    
    def _calculate_lucky_elements(self, birth_chart, transits):
        """Calculate lucky elements for the day"""
        # Generate lucky numbers
        sun_pos = birth_chart.get(const.SUN).lon
        moon_pos = birth_chart.get(const.MOON).lon
        venus_pos = transits.get(const.VENUS).lon
        
        lucky_numbers = [
            int(sun_pos / 30) + 1,  # 1-12
            int(moon_pos / 12) + 1,  # 1-30 
            int(venus_pos / 40) + 1   # 1-9
        ]
        
        # Select colors
        color_index = hash(str(venus_pos)) % len(self.lucky_colors)
        lucky_colors = self.lucky_colors[color_index]
        
        # Select direction
        mars_pos = transits.get(const.MARS).lon
        direction_index = int(mars_pos / 45) % len(self.directions)
        lucky_direction = self.directions[direction_index]
        
        # Select stone
        stone_index = int(moon_pos / 72) % len(self.lucky_stones)
        lucky_stone = self.lucky_stones[stone_index]
        
        return {
            'lucky_numbers': sorted(lucky_numbers),
            'lucky_colors': lucky_colors,
            'lucky_direction': lucky_direction,
            'lucky_stone': lucky_stone
        }
    
    def _calculate_life_areas(self, birth_chart, transits):
        """Calculate life area forecasts with varied analysis"""
        # Calculate ratings with some variation
        base_career = 3.5 + random.uniform(-0.5, 1.5)
        base_love = 3.0 + random.uniform(-0.5, 1.5)
        base_health = 4.0 + random.uniform(-0.5, 1.0)
        base_growth = 4.5 + random.uniform(-0.5, 0.5)
        
        # Career & Finance variations
        career_forecasts = [
            "Today is highly favorable for career advancement with Mercury's influence sharpening your communication skills and strategic thinking. Your creative solutions will be well-received by colleagues and superiors, opening doors to new opportunities. Financial decisions made today have potential for long-term gains, particularly investments in education or technology.",
            
            "Professional networking takes center stage today as Jupiter's aspects enhance your ability to connect with influential people in your field. Your natural leadership qualities shine through in group settings, making this an ideal time for presentations or proposals. Consider diversifying your income streams as new revenue opportunities may present themselves unexpectedly.",
            
            "Saturn's stabilizing energy supports methodical progress toward your career goals, favoring steady advancement over dramatic leaps. Your reputation for reliability and competence continues to grow, attracting the attention of mentors and potential collaborators. Focus on building systems that will support your long-term financial security.",
            
            "Mars energizes your professional ambitions today, giving you the drive to tackle challenging projects that others might avoid. Your competitive edge is sharp, but remember to channel this energy constructively rather than confrontationally. Entrepreneurial ventures receive cosmic support, particularly those involving innovation or technology."
        ]
        
        # Love & Relationships variations  
        love_forecasts = [
            "Venus's harmonious aspects enhance your magnetic appeal and emotional intelligence, making you irresistible to potential partners and deepening bonds with existing ones. Singles may find themselves attracting multiple romantic options, while committed couples discover new depths of intimacy through honest communication. Social gatherings prove particularly fruitful for making meaningful connections.",
            
            "The Moon's influence heightens your intuitive understanding of others' needs and desires, creating opportunities for profound emotional connections. Existing relationships benefit from your increased empathy and willingness to listen without judgment. For those seeking love, trust your instincts about people you meet - your psychic radar is especially accurate today.",
            
            "Pluto's transformative energy may bring intensity to romantic relationships, pushing surface-level connections toward deeper commitment or natural completion. While this might feel overwhelming, these changes ultimately serve your highest good by aligning you with relationships that truly support your growth. Be willing to have difficult but necessary conversations.",
            
            "Jupiter's expansive influence encourages you to broaden your social circle and explore new types of relationships or relationship dynamics. Long-distance connections receive special cosmic support, as do relationships that involve cultural exchange or shared learning experiences. Your optimistic energy attracts like-minded souls who share your vision for the future."
        ]
        
        # Health & Wellness variations
        health_forecasts = [
            "Your physical vitality receives a boost from Mars's energizing influence, making this an excellent day for starting new fitness routines or tackling physically demanding tasks. Mental clarity is exceptionally high, though you may need to guard against overthinking or analysis paralysis. Pay special attention to your nervous system - calming activities like meditation or gentle yoga will help maintain balance.",
            
            "The Moon's connection to your health sector emphasizes the mind-body connection, encouraging you to notice how emotions affect your physical wellbeing. Your digestive system may be more sensitive than usual, so choose nourishing foods that support both your body and mood. Water-based activities or treatments could provide unexpected healing benefits.",
            
            "Saturn's influence reminds you that consistency in health habits yields the best long-term results, favoring gradual lifestyle changes over dramatic interventions. Your discipline and commitment to wellness routines strengthen today, making it easier to stick with beneficial practices. Focus on building habits that will serve you for years to come rather than seeking quick fixes.",
            
            "Uranus brings innovative approaches to health and wellness into your awareness, encouraging you to experiment with new healing modalities or fitness techniques. Your body may respond unusually well to alternative treatments or cutting-edge therapies. Trust your instincts about what your body needs, even if it differs from conventional wisdom."
        ]
        
        # Personal Growth variations
        growth_forecasts = [
            "Today marks a significant phase in your personal evolution as Pluto's transformative energy helps you release outdated beliefs and embrace more authentic ways of being. Your psychological insights are remarkably sharp, allowing you to understand patterns that have been limiting your growth. This is an ideal time for therapy, journaling, or any practice that promotes self-awareness and emotional healing.",
            
            "Jupiter's wisdom-enhancing influence expands your philosophical understanding and spiritual awareness, opening new pathways for personal development. Your ability to see the bigger picture helps you make sense of recent challenges and recognize how they've contributed to your growth. Teaching or mentoring others could provide unexpected insights about your own journey.",
            
            "Neptune's intuitive influence heightens your connection to your inner wisdom and creative potential, making this an excellent time for artistic pursuits or spiritual practices. Your dreams and meditation experiences may contain important messages about your path forward. Trust the subtle guidance you receive through non-rational channels.",
            
            "Mercury's influence supports learning new skills or subjects that genuinely fascinate you, particularly those involving communication, technology, or problem-solving. Your mental agility is enhanced, making it easier to absorb complex information and make innovative connections between different areas of knowledge. Consider taking a class or workshop that challenges your intellect."
        ]
        
        # Tips variations
        career_tips = [
            "Schedule important meetings during your auspicious hours (1-3 PM) for maximum impact and receptivity from colleagues.",
            "Document your innovative ideas today - they have the potential to become valuable intellectual property.",
            "Network authentically rather than transactionally; genuine connections will serve you better than superficial ones.",
            "Focus on problem-solving rather than problem-finding; your solutions-oriented approach will be noticed and appreciated."
        ]
        
        love_tips = [
            "Wear blue or purple to enhance your natural charisma and magnetic appeal in social situations.",
            "Practice vulnerability in your relationships - authentic sharing deepens bonds more than trying to appear perfect.",
            "Listen with your heart as much as your head during important conversations with loved ones.",
            "Plan a surprise gesture that shows thoughtfulness rather than expense - it's the intention that matters most."
        ]
        
        health_tips = [
            "A morning meditation or gentle yoga session will help balance your energy for the day ahead.",
            "Stay hydrated and choose foods that support both your physical energy and emotional wellbeing.",
            "Take regular breaks from screens to rest your eyes and nervous system throughout the day.",
            "Spend time in nature if possible - even a brief walk outdoors can reset your energy and mood."
        ]
        
        growth_tips = [
            "Set aside time for brainstorming or working on a creative project to maximize today's inspirational energy.",
            "Journal about recent experiences to extract valuable lessons and insights for future growth.",
            "Practice mindfulness during routine activities to discover new perspectives on familiar situations.",
            "Engage with material that challenges your current worldview - growth often comes through gentle discomfort."
        ]
        
        return {
            'career_finance': {
                'rating': self._score_to_stars(base_career),
                'forecast': random.choice(career_forecasts),
                'tip': random.choice(career_tips)
            },
            'love_relationships': {
                'rating': self._score_to_stars(base_love),
                'forecast': random.choice(love_forecasts),
                'tip': random.choice(love_tips)
            },
            'health_wellness': {
                'rating': self._score_to_stars(base_health),
                'forecast': random.choice(health_forecasts),
                'tip': random.choice(health_tips)
            },
            'personal_growth': {
                'rating': self._score_to_stars(base_growth),
                'forecast': random.choice(growth_forecasts),
                'tip': random.choice(growth_tips)
            }
        }
    
    def _generate_daily_guidance(self, birth_chart, transits, fortune_score):
        """Generate comprehensive daily guidance"""
        sun_sign = birth_chart.get(const.SUN).sign
        
        # Expanded focus descriptions based on astrological influences
        focus_options = [
            "Today's cosmic energy strongly favors career advancement and financial growth, with planetary alignments creating opportune moments for presenting your ideas to decision-makers. Your creative problem-solving abilities are heightened, making colleagues and superiors more receptive to your innovative approaches. The universe is opening doors to long-term prosperity, so focus on building relationships that will serve your professional goals for years to come. Trust your instincts when it comes to investment opportunities or career moves that seem aligned with your deeper purpose.",
            
            "The celestial influences today create a powerful backdrop for meaningful relationship building and authentic self-expression in all areas of your life. Your natural charisma and communication skills are amplified, drawing people toward you who can offer valuable insights, opportunities, or genuine friendship. Focus on deepening existing connections rather than spreading your energy too thin across surface-level interactions. The universe is supporting heart-centered conversations that could lead to significant personal or professional breakthroughs.",
            
            "Today brings exceptional clarity for strategic planning and visionary thinking, with planetary aspects supporting your ability to see both immediate opportunities and long-term potential. Your analytical capabilities are sharp, while your intuitive faculties provide crucial insights that pure logic might miss. Focus on projects that require both creative inspiration and practical execution, as you're uniquely positioned to bridge these domains. The cosmic energy supports ambitious goal-setting and the development of comprehensive action plans.",
            
            "The astrological climate today strongly supports learning, teaching, and knowledge-sharing activities that could have far-reaching positive impact. Your ability to synthesize complex information and present it in accessible ways is enhanced, making this an ideal time for presentations, workshops, or mentoring relationships. Focus on expanding your expertise in areas that genuinely fascinate you, as passionate learning today could open unexpected career doors tomorrow. The universe is supporting your role as both student and teacher in the grand scheme of life."
        ]
        
        # Expanded challenge descriptions
        challenge_options = [
            "Venus and Mercury's current aspects may create temporary communication misunderstandings, particularly in close relationships where emotions run high and expectations aren't clearly articulated. Practice active listening and avoid making assumptions about others' motivations or intentions during conversations that feel charged or sensitive. The key to navigating these cosmic crosscurrents lies in speaking your truth with compassion while remaining genuinely curious about perspectives that differ from your own. Remember that what feels like conflict today may actually be the universe's way of deepening intimacy and understanding.",
            
            "Mars's influence today could manifest as impatience or frustration with processes that seem unnecessarily slow or bureaucratic, testing your ability to maintain grace under pressure. The cosmic energy may amplify your desire for immediate results, but the universe is actually teaching valuable lessons about timing, persistence, and strategic patience. Channel any restless energy into productive activities like physical exercise, creative projects, or detailed planning for future endeavors. Sometimes apparent delays are actually perfect timing in disguise.",
            
            "Saturn's aspect today may bring encounters with authority figures or institutional structures that challenge your preferred way of operating, requiring diplomacy and adaptive thinking. The universe is presenting opportunities to refine your approach to rules, boundaries, and hierarchical relationships in ways that ultimately serve your long-term goals. Focus on finding win-win solutions rather than engaging in power struggles that drain your energy without creating meaningful change. These cosmic lessons in patience and strategy will pay dividends in future leadership situations.",
            
            "Jupiter's current position may create overconfidence or a tendency to overcommit to too many projects simultaneously, potentially spreading your energy too thin across multiple fronts. The challenge lies in maintaining enthusiasm and optimism while exercising practical discernment about which opportunities truly deserve your precious time and attention. The universe is teaching you the art of conscious choice-making and the power that comes from focusing deeply rather than broadly. Sometimes saying no to good opportunities creates space for great ones to emerge."
        ]
        
        # Randomly select from options to create variety
        focus = random.choice(focus_options)
        challenges = random.choice(challenge_options)
        
        return {
            'focus_of_the_day': focus,
            'challenges_to_navigate': challenges
        }
    
    def _analyze_planet_influence(self, birth_chart, transits, planet_id):
        """Analyze planetary influence"""
        try:
            birth_planet = birth_chart.get(planet_id)
            transit_planet = transits.get(planet_id)
            
            # Basic influence calculation
            influence = random.uniform(-1.0, 2.0)
            return influence
        except:
            return 0.0
    
    def _get_lunar_phase_bonus(self, lunar_phase):
        """Get bonus based on lunar phase"""
        phase_bonuses = {
            'New Moon': 0.5,
            'Waxing Crescent': 0.3,
            'First Quarter': 0.2,
            'Waxing Gibbous': 0.4,
            'Full Moon': 0.6,
            'Waning Gibbous': 0.1,
            'Last Quarter': -0.1,
            'Waning Crescent': 0.0
        }
        return phase_bonuses.get(lunar_phase, 0.0)
    
    def _score_to_stars(self, score):
        """Convert numeric score to star rating"""
        if score >= 4.5:
            return 5
        elif score >= 3.5:
            return 4
        elif score >= 2.5:
            return 3
        elif score >= 1.5:
            return 2
        else:
            return 1 