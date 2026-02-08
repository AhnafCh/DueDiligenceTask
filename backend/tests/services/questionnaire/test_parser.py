"""
Unit tests for Questionnaire Parser.
"""
import pytest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path

# Adjust imports to match project structure if needed
try:
    from src.services.questionnaire.parser import QuestionnaireParser
    from src.services.questionnaire.models import ParsedQuestionnaire, ParsedSection, ParsedQuestion
except ImportError:
    import sys
    sys.path.append("backend")
    from src.services.questionnaire.parser import QuestionnaireParser
    from src.services.questionnaire.models import ParsedQuestionnaire, ParsedSection, ParsedQuestion

@pytest.fixture
def mock_llm_response():
    return ParsedQuestionnaire(
        sections=[
            ParsedSection(
                title="Section 1",
                order=1,
                questions=[
                    ParsedQuestion(
                        text="What is the company name?",
                        order=1,
                        expected_answer_type="text"
                    )
                ]
            )
        ]
    )

def test_parser_init():
    with patch("src.services.questionnaire.parser.ChatGoogleGenerativeAI") as mock_llm:
        parser = QuestionnaireParser()
        assert parser.llm is not None

def test_extract_text_from_pdf():
    # Helper test for pdf extraction logic if exposed,
    # or test parse_file with mock
    pass

@patch("src.services.questionnaire.parser.get_settings")
@patch("src.services.questionnaire.parser.ChatGoogleGenerativeAI")
def test_parse_file_pdf(mock_llm_class, mock_settings):
    # Setup
    mock_settings.return_value.google_api_key = "fake_key"
    
    with patch("src.services.questionnaire.parser.PyPDF2.PdfReader") as mock_pdf_reader:
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Page text"
        mock_pdf_reader.return_value.pages = [mock_page]
        
        parser = QuestionnaireParser()
        
        # Mock _extract_structure_with_llm to avoid real LLM call
        parsed_q = ParsedQuestionnaire(sections=[])
        parser._extract_structure_with_llm = MagicMock(return_value=parsed_q)
        
        with patch("builtins.open", mock_open(read_data=b"pdf_content")):
            result = parser.parse_file(Path("test.pdf"))
            
        parser._extract_structure_with_llm.assert_called_once()
        assert result == parsed_q

