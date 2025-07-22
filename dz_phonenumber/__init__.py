"""

@author : Aymen Brahim Djelloul
@version : 0.1
@date : 18.07.2025
@license : MIT License


    // Sources :
     - https://en.wikipedia.org/wiki/Telephone_numbers_in_Algeria
     - https://www.howtocallabroad.com/algeria/

"""

# IMPORTS
import sys
import re
from dataclasses import dataclass
from typing import Optional, Dict, Tuple, Union
import zoneinfo


@dataclass
class GeoCoder:
    """Represents a geographical region with landline phone codes and timezone."""
    name: str
    longitude: float = 0.0
    latitude: float = 0.0
    altitude: float = 0.0
    timezone: str = "Africa/Algiers"


class _Const:
    """Comprehensive Algerian telecommunications data repository."""

    # Country identifiers
    COUNTRY_CODE: str = '+213'
    INTERNATIONAL_PREFIX: str = '00'
    NATIONAL_PREFIX: str = '0'
    TRUNK_PREFIX: str = '0'

    # Number patterns
    LANDLINE_PATTERNS: Tuple[str, ...] = ('2', '3', '4')
    MOBILE_PATTERNS: Tuple[str, ...] = ('5', '6', '7')
    SPECIAL_PATTERNS: Tuple[str, ...] = ('8', '9')

    # Mobile carriers
    MOBILE_CARRIERS: Dict[str, str] = {
        '5': 'Ooredoo',
        '6': 'Mobilis',
        '7': 'Djezzy',
    }

    # Number lengths
    NUMBER_LENGTHS: Dict[str, Union[int, Tuple[int, ...]]] = {
        'mobile': 9,
        'landline': 8,
        'voip': 8,
        'vsat': 8,
        'short_code': 4,
        'emergency': (2, 3, 4)  # Variable length
    }

    # Landline regions with geographic data
    LANDLINE_REGIONS: Dict[str, GeoCoder] = {
        '49': GeoCoder("Adrar", -0.2936, 27.8743, 258),
        '27': GeoCoder("Ain Defla", 1.9594, 36.2509, 190),
        '43': GeoCoder("Ain Temouchent", -1.1400, 35.2970, 120),
        '21': GeoCoder("Algiers", 3.0588, 36.7538, 10),
        '38': GeoCoder("Annaba", 7.7667, 36.9000, 3),
        '33': GeoCoder("Batna", 6.1697, 35.5559, 1048),
        '34': GeoCoder("Bejaia", 5.0667, 36.7500, 2),
        '25': GeoCoder("Blida", 2.8276, 36.4700, 260),
        '35': GeoCoder("Bordj Bou Arreridj", 4.7611, 36.0736, 928),
        '26': GeoCoder("Bouira", 3.9000, 36.3667, 519),
        '24': GeoCoder("Boumerdes", 3.4772, 36.7664, 10),
        '27': GeoCoder("Chlef", 1.3319, 36.1654, 114),
        '31': GeoCoder("Constantine", 6.6147, 36.3650, 694),
        '27': GeoCoder("Djelfa", 3.2500, 34.6667, 1143),
        '32': GeoCoder("El Oued", 6.8639, 33.3683, 76),
        '29': GeoCoder("Ghardaia", 3.6736, 32.4839, 572),
        '37': GeoCoder("Guelma", 7.4264, 36.4614, 290),
        '29': GeoCoder("Illizi", 8.4667, 26.4833, 558),
        '34': GeoCoder("Jijel", 5.7667, 36.8167, 10),
        '32': GeoCoder("Khenchela", 7.1464, 35.4269, 1122),
        '29': GeoCoder("Laghouat", 2.8667, 33.8000, 769),
        '35': GeoCoder("M'sila", 4.5333, 35.7000, 471),
        '45': GeoCoder("Mascara", 0.1408, 35.4000, 570),
        '25': GeoCoder("Medea", 2.7583, 36.2675, 920),
        '31': GeoCoder("Mila", 6.2647, 36.4503, 470),
        '45': GeoCoder("Mostaganem", 0.0892, 35.9333, 104),
        '41': GeoCoder("Oran", -0.6333, 35.6911, 101),
        '29': GeoCoder("Ouargla", 5.3333, 31.9500, 141),
        '32': GeoCoder("Oum El Bouaghi", 7.1136, 35.8778, 902),
        '46': GeoCoder("Relizane", 0.5558, 35.7372, 98),
        '48': GeoCoder("Saida", 4.8306, 34.8303, 870),
        '36': GeoCoder("Setif", 5.4089, 36.1919, 1096),
        '48': GeoCoder("Sidi Bel Abbes", -0.6333, 35.2000, 470),
        '38': GeoCoder("Skikda", 6.9094, 36.8667, 18),
        '37': GeoCoder("Souk Ahras", 7.9514, 36.2864, 699),
        '29': GeoCoder("Tamanrasset", 5.5167, 22.7850, 1320),
        '37': GeoCoder("Tebessa", 8.1206, 35.4072, 858),
        '46': GeoCoder("Tiaret", 1.3167, 35.3667, 1032),
        '43': GeoCoder("Tlemcen", -1.3139, 34.8828, 842),
        '24': GeoCoder("Tipaza", 2.4500, 36.5833, 120),
        '46': GeoCoder("Tissemsilt", 1.8000, 35.6000, 850),
        '26': GeoCoder("Tizi Ouzou", 4.0500, 36.7167, 200)
    }

    # Emergency services
    EMERGENCY_NUMBERS: Dict[str, str] = {
        '1548': 'Police Nationale',
        '17': 'Police (Short Code)',
        '1055': 'Gendarmerie Nationale',
        '1054': 'Coast Guard',
        '14': 'Protection Civile',
        '1021': 'Civil Protection',
        '1040': 'SAMU (Emergency Medical)',
        '1234': 'Electricity Emergency',
        '1235': 'Gas Emergency',
    }

    # Special services
    SPECIAL_NUMBERS: Dict[str, str] = {
        '98': 'VOIP',
        '96': 'VSAT',
        '97': 'IoT/M2M Services',
    }


class PhoneNumber:
    """Algerian phone number parser and validator."""

    def __init__(self, number: str):
        self.original_number = number
        self.clean_number = self._normalize_number(number)
        self.number_type = None
        self.area_code = None
        self.carrier = None
        self.location = None
        self.is_valid = False

        self._parse_number()

    def _normalize_number(self, number: str) -> str:
        """Remove all non-digit characters from the number."""
        return re.sub(r'[^\d+]', '', number)

    def _parse_number(self):
        """Parse and validate the phone number."""
        num = self.clean_number

        # Check for international format
        if num.startswith('213'):
            num = num[3:]
        elif num.startswith('+213'):
            num = num[4:]

        # Remove national prefix if present
        if num.startswith('0'):
            num = num[1:]

        # Determine number type
        if len(num) in (2, 3, 4) and num in _Const.EMERGENCY_NUMBERS:
            self.number_type = 'emergency'
            self.is_valid = True

        elif len(num) == _Const.NUMBER_LENGTHS['mobile']:
            self._parse_mobile(num)

        elif len(num) == _Const.NUMBER_LENGTHS['landline']:
            self._parse_landline(num)

        elif len(num) == _Const.NUMBER_LENGTHS['voip'] and num.startswith('98'):
            self.number_type = 'voip'
            self.is_valid = True

        elif len(num) == _Const.NUMBER_LENGTHS['vsat'] and num.startswith('96'):
            self.number_type = 'vsat'
            self.is_valid = True

        else:
            self.is_valid = False

    def _parse_mobile(self, num: str):
        """Parse mobile phone numbers."""
        if num[0] in _Const.MOBILE_PATTERNS:
            self.number_type = 'mobile'
            self.carrier = _Const.MOBILE_CARRIERS.get(num[0], 'Unknown')
            self.is_valid = True

    def _parse_landline(self, num: str):
        """Parse landline phone numbers."""
        if num[0] in _Const.LANDLINE_PATTERNS:
            area_code = num[:2]
            if area_code in _Const.LANDLINE_REGIONS:
                self.number_type = 'landline'
                self.area_code = area_code
                self.location = _Const.LANDLINE_REGIONS[area_code]
                self.is_valid = True

    def is_mobile(self) -> bool:
        """Check if the number is a mobile number."""
        return self.number_type == 'mobile'

    def is_landline(self) -> bool:
        """Check if the number is a landline."""
        return self.number_type == 'landline'

    def is_emergency(self) -> bool:
        """Check if the number is an emergency number."""
        return self.number_type == 'emergency'

    def is_voip(self) -> bool:
        """Check if the number is a VOIP number."""
        return self.number_type == 'voip'

    def is_vsat(self) -> bool:
        """Check if the number is a VSAT number."""
        return self.number_type == 'vsat'

    def get_all_info(self) -> Dict:
        """Get all available information about the phone number."""
        return {
            'original_number': self.original_number,
            'clean_number': self.clean_number,
            'type': self.number_type,
            'valid': self.is_valid,
            'carrier': self.carrier,
            'area_code': self.area_code,
            'location': self.location.name if self.location else None,
            'coordinates': (self.location.longitude, self.location.latitude) if self.location else None,
            'timezone': self.location.timezone if self.location else None
        }

    def __str__(self) -> str:
        """String representation of the phone number information."""
        if not self.is_valid:
            return f"Invalid Algerian phone number: {self.original_number}"

        info = self.get_all_info()
        parts = [
            f"Algerian Phone Number: {self.clean_number}",
            f"Type: {info['type'].upper()}",
        ]

        if self.carrier:
            parts.append(f"Carrier: {self.carrier}")
        if self.area_code:
            parts.append(f"Area Code: {self.area_code}")
        if self.location:
            parts.append(f"Location: {info['location']}")
            parts.append(f"Coordinates: {info['coordinates']}")

        return "\n".join(parts)


class Formatter:
    pass


__all__ = ['PhoneNumber', 'Formatter']

if __name__ == '__main__':
    sys.exit(0)
