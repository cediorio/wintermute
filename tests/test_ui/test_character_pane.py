"""Tests for the CharacterPane widget."""

import pytest
from textual.app import App

from wintermute.models.character import Character
from wintermute.ui.character_pane import CharacterPane


class PersonaPaneTestApp(App):
    """Test app for CharacterPane."""

    def __init__(self, characters: list[Character] | None = None):
        super().__init__()
        self.test_characters = characters or []

    def compose(self):
        """Compose the test app."""
        yield CharacterPane(self.test_characters)


@pytest.fixture
def sample_characters() -> list[Character]:
    """Create sample characters for testing."""
    return [
        Character(
            id="default",
            name="Default Assistant",
            system_prompt="You are helpful.",
            description="A balanced assistant",
        ),
        Character(
            id="technical",
            name="Technical Expert",
            system_prompt="You are technical.",
            description="Expert in programming",
            temperature=0.5,
        ),
        Character(
            id="creative",
            name="Creative Writer",
            system_prompt="You are creative.",
            description="Creative and imaginative",
            temperature=0.9,
        ),
    ]


class TestCharacterPaneInitialization:
    """Test CharacterPane initialization."""

    @pytest.mark.asyncio
    async def test_persona_pane_can_be_created(self, sample_characters):
        """Test that CharacterPane can be instantiated."""
        pane = CharacterPane(sample_characters)
        assert pane is not None

    @pytest.mark.asyncio
    async def test_persona_pane_stores_characters(self, sample_characters):
        """Test that CharacterPane stores the provided characters."""
        pane = CharacterPane(sample_characters)
        assert len(pane.characters) == 3
        assert pane.characters[0].id == "default"

    @pytest.mark.asyncio
    async def test_persona_pane_with_empty_list(self):
        """Test that CharacterPane works with empty character list."""
        pane = CharacterPane([])
        assert len(pane.characters) == 0

    @pytest.mark.asyncio
    async def test_character_pane_initial_selection(self, sample_characters):
        """Test that first character is selected by default."""
        pane = CharacterPane(sample_characters)
        assert pane.selected_index == 0
        assert pane.get_selected_character().id == "default"


class TestCharacterPaneRendering:
    """Test CharacterPane rendering."""

    @pytest.mark.asyncio
    async def test_persona_pane_renders_in_app(self, sample_characters):
        """Test that CharacterPane renders correctly in app."""
        app = PersonaPaneTestApp(sample_characters)
        async with app.run_test() as pilot:
            await pilot.pause()
            
            persona_pane = app.query_one(CharacterPane)
            assert persona_pane is not None

    @pytest.mark.asyncio
    async def test_persona_pane_displays_persona_names(self, sample_characters):
        """Test that CharacterPane displays all character names."""
        app = PersonaPaneTestApp(sample_characters)
        async with app.run_test() as pilot:
            await pilot.pause()
            
            persona_pane = app.query_one(CharacterPane)
            rendered = persona_pane.render()
            rendered_str = str(rendered)
            
            assert "Default Assistant" in rendered_str
            assert "Technical Expert" in rendered_str
            assert "Creative Writer" in rendered_str

    @pytest.mark.asyncio
    async def test_persona_pane_highlights_selected(self, sample_characters):
        """Test that CharacterPane highlights the selected character."""
        app = PersonaPaneTestApp(sample_characters)
        async with app.run_test() as pilot:
            await pilot.pause()
            
            persona_pane = app.query_one(CharacterPane)
            rendered = persona_pane.render()
            # Selected character should have some visual indication
            assert rendered is not None


class TestCharacterPaneSelection:
    """Test CharacterPane selection functionality."""

    @pytest.mark.asyncio
    async def test_select_character_by_index(self, sample_characters):
        """Test selecting a character by index."""
        pane = CharacterPane(sample_characters)
        
        pane.select_character(1)
        
        assert pane.selected_index == 1
        assert pane.get_selected_character().id == "technical"

    @pytest.mark.asyncio
    async def test_select_character_by_id(self, sample_characters):
        """Test selecting a character by ID."""
        pane = CharacterPane(sample_characters)
        
        pane.select_character_by_id("creative")
        
        assert pane.selected_index == 2
        assert pane.get_selected_character().id == "creative"

    @pytest.mark.asyncio
    async def test_select_invalid_index(self, sample_characters):
        """Test that selecting invalid index does nothing."""
        pane = CharacterPane(sample_characters)
        original_index = pane.selected_index
        
        pane.select_character(99)
        
        # Should remain unchanged
        assert pane.selected_index == original_index

    @pytest.mark.asyncio
    async def test_select_negative_index(self, sample_characters):
        """Test that selecting negative index does nothing."""
        pane = CharacterPane(sample_characters)
        original_index = pane.selected_index
        
        pane.select_character(-1)
        
        # Should remain unchanged
        assert pane.selected_index == original_index

    @pytest.mark.asyncio
    async def test_select_character_by_invalid_id(self, sample_characters):
        """Test that selecting by invalid ID does nothing."""
        pane = CharacterPane(sample_characters)
        original_index = pane.selected_index
        
        pane.select_character_by_id("nonexistent")
        
        # Should remain unchanged
        assert pane.selected_index == original_index


class TestCharacterPaneNavigation:
    """Test CharacterPane navigation."""

    @pytest.mark.asyncio
    async def test_next_character(self, sample_characters):
        """Test navigating to next character."""
        pane = CharacterPane(sample_characters)
        
        pane.next_character()
        
        assert pane.selected_index == 1

    @pytest.mark.asyncio
    async def test_previous_character(self, sample_characters):
        """Test navigating to previous character."""
        pane = CharacterPane(sample_characters)
        pane.select_character(1)
        
        pane.previous_character()
        
        assert pane.selected_index == 0

    @pytest.mark.asyncio
    async def test_next_character_wraps_around(self, sample_characters):
        """Test that next_persona wraps to beginning."""
        pane = CharacterPane(sample_characters)
        pane.select_character(2)  # Last character
        
        pane.next_character()
        
        assert pane.selected_index == 0

    @pytest.mark.asyncio
    async def test_previous_character_wraps_around(self, sample_characters):
        """Test that previous_persona wraps to end."""
        pane = CharacterPane(sample_characters)
        pane.select_character(0)  # First character
        
        pane.previous_character()
        
        assert pane.selected_index == 2


class TestCharacterPaneGetters:
    """Test CharacterPane getter methods."""

    @pytest.mark.asyncio
    async def test_get_selected_character(self, sample_characters):
        """Test getting the currently selected character."""
        pane = CharacterPane(sample_characters)
        pane.select_character(1)
        
        selected = pane.get_selected_character()
        
        assert selected.id == "technical"
        assert selected.name == "Technical Expert"

    @pytest.mark.asyncio
    async def test_get_all_characters(self, sample_characters):
        """Test getting all characters."""
        pane = CharacterPane(sample_characters)
        
        all_characters = pane.get_all_characters()
        
        assert len(all_characters) == 3
        assert all_characters[0].id == "default"
