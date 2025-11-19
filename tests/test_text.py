"""Tests for text processing utilities."""

from xtract.utils.text import expand_urls


class TestExpandUrls:
    """Test suite for expand_urls function."""

    def test_expand_single_url(self):
        """Test expanding a single t.co URL."""
        text = "Check this out: https://t.co/abc123"
        url_entities = [
            {
                "url": "https://t.co/abc123",
                "expanded_url": "https://example.com/article",
            }
        ]

        result = expand_urls(text, url_entities)
        assert result == "Check this out: https://example.com/article"

    def test_expand_multiple_urls(self):
        """Test expanding multiple t.co URLs in one text."""
        text = "Visit https://t.co/abc123 and https://t.co/def456 for more info"
        url_entities = [
            {
                "url": "https://t.co/abc123",
                "expanded_url": "https://example.com/page1",
            },
            {
                "url": "https://t.co/def456",
                "expanded_url": "https://example.com/page2",
            },
        ]

        result = expand_urls(text, url_entities)
        assert (
            result == "Visit https://example.com/page1 and https://example.com/page2 for more info"
        )

    def test_url_with_trailing_comma(self):
        """Test URL followed by a comma (punctuation should remain)."""
        text = "Check https://t.co/abc123, it's great!"
        url_entities = [
            {
                "url": "https://t.co/abc123",
                "expanded_url": "https://example.com",
            }
        ]

        result = expand_urls(text, url_entities)
        assert result == "Check https://example.com, it's great!"

    def test_url_with_trailing_period(self):
        """Test URL followed by a period (punctuation should remain)."""
        text = "Visit https://t.co/abc123."
        url_entities = [
            {
                "url": "https://t.co/abc123",
                "expanded_url": "https://example.com/page",
            }
        ]

        result = expand_urls(text, url_entities)
        assert result == "Visit https://example.com/page."

    def test_url_at_end_of_sentence(self):
        """Test URL at the end of a sentence with multiple punctuation."""
        text = "Have you seen this? https://t.co/xyz789!"
        url_entities = [
            {
                "url": "https://t.co/xyz789",
                "expanded_url": "https://example.com/article",
            }
        ]

        result = expand_urls(text, url_entities)
        assert result == "Have you seen this? https://example.com/article!"

    def test_empty_url_entities(self):
        """Test with empty URL entities list."""
        text = "No URLs here"
        url_entities = []

        result = expand_urls(text, url_entities)
        assert result == "No URLs here"

    def test_missing_url_field(self):
        """Test graceful handling of entity with missing 'url' field."""
        text = "Check https://t.co/abc123"
        url_entities = [
            {
                "expanded_url": "https://example.com",
                # Missing 'url' field
            }
        ]

        result = expand_urls(text, url_entities)
        # Should return original text since entity is invalid
        assert result == "Check https://t.co/abc123"

    def test_missing_expanded_url_field(self):
        """Test graceful handling of entity with missing 'expanded_url' field."""
        text = "Check https://t.co/abc123"
        url_entities = [
            {
                "url": "https://t.co/abc123",
                # Missing 'expanded_url' field
            }
        ]

        result = expand_urls(text, url_entities)
        # Should return original text since entity is invalid
        assert result == "Check https://t.co/abc123"

    def test_url_not_in_text(self):
        """Test when entity URL doesn't appear in text."""
        text = "Check https://t.co/abc123"
        url_entities = [
            {
                "url": "https://t.co/xyz789",  # Different URL
                "expanded_url": "https://example.com",
            }
        ]

        result = expand_urls(text, url_entities)
        # Should return original text since URL doesn't match
        assert result == "Check https://t.co/abc123"

    def test_special_characters_in_url(self):
        """Test URL with special characters that need escaping."""
        text = "Check https://t.co/abc123"
        url_entities = [
            {
                "url": "https://t.co/abc123",
                "expanded_url": "https://example.com/page?id=1&type=article",
            }
        ]

        result = expand_urls(text, url_entities)
        assert result == "Check https://example.com/page?id=1&type=article"

    def test_url_appears_multiple_times(self):
        """Test same t.co URL appearing multiple times in text."""
        text = "Visit https://t.co/abc123 or https://t.co/abc123 again"
        url_entities = [
            {
                "url": "https://t.co/abc123",
                "expanded_url": "https://example.com",
            }
        ]

        result = expand_urls(text, url_entities)
        assert result == "Visit https://example.com or https://example.com again"

    def test_real_world_example(self):
        """Test with a realistic tweet example."""
        text = "Just published a new article about Python! Check it out: https://t.co/ks152HcHV6"
        url_entities = [
            {
                "url": "https://t.co/ks152HcHV6",
                "expanded_url": "https://grokipedia.com/python-tips",
                "display_url": "grokipedia.com/python-tips",
            }
        ]

        result = expand_urls(text, url_entities)
        assert (
            result
            == "Just published a new article about Python! Check it out: https://grokipedia.com/python-tips"
        )

    def test_url_in_middle_of_word_boundary(self):
        """Test URL with proper word boundaries (parentheses, quotes, etc.)."""
        text = "See (https://t.co/abc123) for details"
        url_entities = [
            {
                "url": "https://t.co/abc123",
                "expanded_url": "https://example.com",
            }
        ]

        result = expand_urls(text, url_entities)
        assert result == "See (https://example.com) for details"

    def test_none_url_entities(self):
        """Test with None url_entities (defensive programming)."""
        text = "Some text"
        # This shouldn't happen in practice, but test defensive behavior
        result = expand_urls(text, None or [])
        assert result == "Some text"

    def test_mixed_valid_and_invalid_entities(self):
        """Test with a mix of valid and invalid entities."""
        text = "Check https://t.co/abc123 and https://t.co/def456"
        url_entities = [
            {
                "url": "https://t.co/abc123",
                "expanded_url": "https://example.com/page1",
            },
            {
                # Missing expanded_url
                "url": "https://t.co/def456",
            },
        ]

        result = expand_urls(text, url_entities)
        # First URL should be expanded, second should remain as-is
        assert result == "Check https://example.com/page1 and https://t.co/def456"
