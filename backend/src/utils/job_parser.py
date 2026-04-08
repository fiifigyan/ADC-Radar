"""Smart text parser for job data extraction from concatenated strings"""
import re
from typing import Dict, List, Tuple

class JobTextParser:
    """Intelligently parse concatenated job text into components"""
    
    # Known organization patterns and keywords
    ORG_KEYWORDS = [
        'International', 'Organization', 'Organisation', 'Agency', 'Council', 
        'Foundation', 'Bank', 'Institute', 'Committee', 'Corp', 'Company',
        'Network', 'Initiative', 'Programme', 'Project', 'Centre', 'Center',
        'Consortium', 'Alliance', 'Association', 'Society', 'Union',
        'WHO', 'UNDP', 'UNEP', 'UNICEF', 'WFP', 'UNHCR', 'UNRWA', 'IRC', 
        'ICRC', 'IOM', 'UNESCO', 'UNFPA', 'UNODC', 'UNOPS', 'UNCDF', 'UNCTAD'
    ]
    
    # Known location keywords
    LOCATION_KEYWORDS = ['Remote', 'Hybrid', 'Home Based', 'Based In']
    
    # Level/contract indicators to remove
    LEVEL_KEYWORDS = [
        'Senior', 'Mid', 'Junior', 'Entry', 'Internship', 'Intern',
        'level', 'Level', 'Temporary', 'Contract', 'Consultant', 'Associate',
        'GS-', 'P-', 'P2', 'P3', 'P4'
    ]
    
    # Common job title words
    TITLE_WORDS = [
        'Manager', 'Coordinator', 'Officer', 'Specialist', 'Analyst',
        'Developer', 'Engineer', 'Consultant', 'Advisor', 'Director',
        'Head', 'Lead', 'Deputy', 'Assistant', 'Adviser', 'Expert',
        'Programme', 'Program', 'Business', 'Operations', 'Technical',
        'Finance', 'Health', 'Education', 'Advocacy', 'Communications',
        'Research', 'Monitoring', 'Evaluation', 'Development', 'Driver',
        'Accountant', 'Procurement', 'Human Resources', 'Security', 'Safety'
    ]
    
    @staticmethod
    def remove_level_indicators(text: str) -> str:
        """Remove level/contract indicators from text"""
        # Pattern for level descriptors at the end
        pattern = r'\s*(Senior\s*-?\s*Senior\s*level|Junior\s*-?\s*Junior\s*level|Mid\s*-?\s*Mid\s*level|Internship|Contract.*|Consultant|Temporary|Pattern.*|GS-\d+.*|P[2-5].*|No.*education.*|Level.*\d+.*|Director General|Adviser|Expert).*$'
        result = re.sub(pattern, '', text, flags=re.IGNORECASE)
        return result.strip()
    
    @staticmethod
    def find_org_boundary(text: str, title: str = '') -> Tuple[int, str]:
        """Find where organization starts in text"""
        text_lower = text.lower()
        
        # Look for explicit org keywords
        for keyword in JobTextParser.ORG_KEYWORDS:
            idx = text_lower.find(keyword.lower())
            if idx > 0:
                # Find the start of this word to avoid cutting mid-word
                while idx > 0 and text[idx - 1].isalnum():
                    idx -= 1
                # Backtrack to find the start of this component
                while idx > 0 and text[idx - 1] not in ' |-':
                    idx -= 1
                return idx, keyword
        
        # If title was found, org likely starts right after
        if title and title in text:
            idx = text.find(title) + len(title)
            return idx, None
        
        return -1, None
    
    @staticmethod
    def find_location_boundary(text: str) -> Tuple[int, str]:
        """Find where location starts in text"""
        text_lower = text.lower()
        
        # Look for explicit location keywords
        for keyword in JobTextParser.LOCATION_KEYWORDS:
            idx = text_lower.find(keyword.lower())
            if idx >= 0:
                return idx, keyword
        
        # Look for pipes or common location patterns
        if '|' in text:
            idx = text.find('|')
            while idx > 0 and text[idx - 1] == ' ':
                idx -= 1
            return idx, None
        
        return -1, None
    
    @staticmethod
    def extract_title_candidate(text: str, max_length: int = 100) -> str:
        """Extract potential title from text start"""
        # Title is usually the beginning of text
        # Look for transitions in character case as boundaries
        words = []
        current_word = []
        
        for i, char in enumerate(text[:max_length]):
            if char in ' -|,':
                if current_word:
                    words.append(''.join(current_word))
                    current_word = []
                # Keep a single space
                if char == ' ':
                    words.append(' ')
            elif i > 0 and text[i - 1].islower() and char.isupper() and len(current_word) > 0:
                # Case transition - might be word boundary
                words.append(''.join(current_word))
                current_word = [char]
            else:
                current_word.append(char)
        
        if current_word:
            words.append(''.join(current_word))
        
        title_candidate = ''.join(words).strip()
        
        # Limit length and clean
        if len(title_candidate) > max_length:
            title_candidate = title_candidate[:max_length].rsplit(' ', 1)[0]
        
        return title_candidate
    
    @staticmethod
    def validate_organization(text: str) -> bool:
        """Check if text looks like an organization"""
        if len(text) < 2:
            return False
        
        # Has org keywords
        for keyword in JobTextParser.ORG_KEYWORDS:
            if keyword.lower() in text.lower():
                return True
        
        # Acronyms (all caps, 3-5 chars)
        if text.isupper() and 2 < len(text) < 6:
            return True
        
        # Multiple capitalized words
        has_caps = sum(1 for word in text.split() if word and word[0].isupper())
        if has_caps >= 2:
            return True
        
        return False
    
    @staticmethod
    def extract_components(text: str) -> Dict[str, str]:
        """Parse text and extract title, organization, location using case transitions"""
        
        if not text or len(text) < 5:
            return {
                'title': 'Untitled Opportunity',
                'organization': 'Unknown Organization',
                'location': '',
            }
        
        original_text = text
        text = text.strip()
        
        # Remove level/contract indicators first
        text = JobTextParser.remove_level_indicators(text)
        
        title = ''
        organization = ''
        location = ''
        
        # Step 1: Extract location (easiest - has clear keywords or comes after pipes)
        if '|' in text:
            parts = text.split('|', 1)
            text = parts[0].strip()
            location = parts[1].strip()
        else:
            # Look for location keywords like Remote, Hybrid
            for keyword in JobTextParser.LOCATION_KEYWORDS:
                idx = text.lower().find(keyword.lower())
                if idx >= 0:
                    location = text[idx:].strip()
                    text = text[:idx].strip()
                    break
        
        # Step 2: Split remaining text at case transitions
        # Pattern: lowercase letter followed by uppercase (e.g., "tW" becomes "t|W")
        # This helps us find component boundaries like "DevelopmentWorld" → "Development|World"
        parts = []
        current = []
        
        for i, char in enumerate(text):
            if i > 0 and text[i-1].islower() and char.isupper():
                # Case transition
                if current:
                    parts.append(''.join(current))
                    current = [char]
                else:
                    current.append(char)
            else:
                current.append(char)
        
        if current:
            parts.append(''.join(current))
        
        parts = [p.strip() for p in parts if p.strip()]
        
        # Step 3: Classify parts - group title parts together
        # Title typically: contains title keywords OR is 1-2 words
        # Organization: has org keywords OR is 2-4 words properly-cased
        
        if len(parts) == 0:
            title = text
        elif len(parts) == 1:
            # Single part - is it a title or org?
            if any(kw.lower() in parts[0].lower() for kw in JobTextParser.ORG_KEYWORDS):
                organization = parts[0]
            else:
                title = parts[0]
        elif len(parts) == 2:
            # Two parts - first is usually title, second is org
            title = parts[0]
            organization = parts[1]
        
        else:  # len(parts) >= 3
            # Multiple parts: group title words together, then org
            title_parts = [parts[0]]
            remaining_idx = 1
            
            # Keep adding parts to title if they contain title keywords
            for i in range(1, len(parts)):
                part = parts[i]
                has_title_word = any(kw.lower() in part.lower() for kw in JobTextParser.TITLE_WORDS)
                has_org_word = any(kw.lower() in part.lower() for kw in JobTextParser.ORG_KEYWORDS)
                
                # If it has title words and not org words, add to title
                if has_title_word and not has_org_word:
                    title_parts.append(part)
                    remaining_idx = i + 1
                # Short parts (1-3 chars) like "UK", "USA" might be location junk - skip them
                elif len(part) <= 3:
                    continue
                else:
                    # This is likely the start of org
                    remaining_idx = i
                    break
            
            title = ' '.join(title_parts)
            
            # Organization is composed of remaining parts
            # Take next 2-3 parts (usually org is 2-4 words)
            if remaining_idx < len(parts):
                # Take up to 2 parts for org (orgs are usually 2-3 words like "World Vision Australia")
                org_parts = []
                for i in range(remaining_idx, min(remaining_idx + 2, len(parts))):
                    org_parts.append(parts[i])
                
                org_candidate = ' '.join(org_parts)
                if org_candidate and len(org_candidate) >= 2:
                    organization = org_candidate
        
        # Step 4: Clean up and validate
        title = title.strip()
        organization = organization.strip()
        location = location.strip()
        
        # Remove remaining dashes and artifacts
        title = re.sub(r'\s*[-–—]\s*$', '', title).strip()
        organization = re.sub(r'\s*[-–—]\s*$', '', organization).strip()
        
        # Ensure minimum quality
        if not title or len(title) < 3:
            title = 'Untitled Opportunity'
        if not organization or len(organization) < 2:
            organization = 'Unknown Organization'
        
        return {
            'title': title,
            'organization': organization,
            'location': location,
        }


def test_parser():
    """Test the parser on sample data"""
    test_cases = [
        "Digital Assets Regulation - AssociateFinancial Innovation for ImpactRemote | Philippines | Indonesia",
        "Head of Business DevelopmentWorld Vision AustraliaMelbourneSenior - Senior level",
        "Business Development ConsultantSmarter GoodRemote | Home Based - May require travel | Mexico | Peru",
        "Economic Recovery OfficerDRC - Danish Refugee CouncilKarakLevel not specified",
        "Political AdviserICRC - International Committee of the Red CrossKassalaSenior - Senior level",
        "ProjectOfficerWHO - World Health OrganizationGeneva",
        "Driver WHO - World Health OrganizationGS-2, General Service - No need for Higher Education - Locally",
    ]
    
    parser = JobTextParser()
    
    print("Testing Job Text Parser (Pattern-Based)")
    print("=" * 80)
    
    correct = 0
    for i, text in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"Input: {text[:85]}...")
        
        result = parser.extract_components(text)
        
        print(f"✓ Title: {result['title']}")
        print(f"  Org: {result['organization']}")
        print(f"  Location: {result['location']}")


if __name__ == "__main__":
    test_parser()

