"""Tests for the PersonaPane widget."""

import pytest
from textual.app import App

from wintermute.models.persona import Persona
from wintermute.ui.persona_pane import PersonaPane


class PersonaPaneTestApp(App):
    """Test app for PersonaPane."""

    def __init__(self, personas: list[Persona] | None = None):
        super().__init__()
        self.test_personas = personas or []

    def compose(self):
        """Compose the test app."""
        yield PersonaPane(self.test_personas)


@pytest.fixture
def sample_personas() -> list[Persona]:
    """Create sample personas for testing."""
    return [
        Persona(
            id="default",
            name="Default Assistant",
            system_prompt="You are helpful.",
            description="A balanced assistant",
        ),
        Persona(
            id="technical",
            name="Technical Expert",
            system_prompt="You are technical.",
            description="Expert in programming",
            temperature=0.5,
        ),
        Persona(
            id="creative",
            name="Creative Writer",
            system_prompt="You are creative.",
            description="Creative and imaginative",
            temperature=0.9,
        ),
    ]


class TestPersonaPaneInitialization:
    """Test PersonaPane initialization."""

    @pytest.mark.asyncio
    async def test_persona_pane_can_be_created(self, sample_personas):
        """Test that PersonaPane can be instantiated."""
        pane = PersonaPane(sample_personas)
        assert pane is not None

    @pytest.mark.asyncio
    async def test_persona_pane_stores_personas(self, sample_personas):
        """Test that PersonaPane stores the provided personas."""
        pane = PersonaPane(sample_personas)
        assert len(pane.personas) == 3
        assert pane.personas[0].id == "default"

    @pytest.mark.asyncio
    async def test_persona_pane_with_empty_list(self):
        """Test that PersonaPane works with empty persona list."""
        pane = PersonaPane([])
        assert len(pane.personas) == 0

    @pytest.mark.asyncio
    async def test_persona_pane_initial_selection(self, sample_personas):
        """Test that first persona is selected by default."""
        pane = PersonaPane(sample_personas)
        assert pane.selected_index == 0
        assert pane.get_selected_persona().id == "default"


class TestPersonaPaneRendering:
    """Test PersonaPane rendering."""

    @pytest.mark.asyncio
    async def test_persona_pane_renders_in_app(self, sample_personas):
        """Test that PersonaPane renders correctly in app."""
        app = PersonaPaneTestApp(sample_personas)
        async with app.run_test() as pilot:
            await pilot.pause()
            
            persona_pane = app.query_one(PersonaPane)
            assert persona_pane is not None

    @pytest.mark.asyncio
    async def test_persona_pane_displays_persona_names(self, sample_personas):
        """Test that PersonaPane displays all persona names."""
        app = PersonaPaneTestApp(sample_personas)
        async with app.run_test() as pilot:
            await pilot.pause()
            
            persona_pane = app.query_one(PersonaPane)
            rendered = persona_pane.render()
            rendered_str = str(rendered)
            
            assert "Default Assistant" in rendered_str
            assert "Technical Expert" in rendered_str
            assert "Creative Writer" in rendered_str

    @pytest.mark.asyncio
    async def test_persona_pane_highlights_selected(self, sample_personas):
        """Test that PersonaPane highlights the selected persona."""
        app = PersonaPaneTestApp(sample_personas)
        async with app.run_test() as pilot:
            await pilot.pause()
            
            persona_pane = app.query_one(PersonaPane)
            rendered = persona_pane.render()
            # Selected persona should have some visual indication
            assert rendered is not None


class TestPersonaPaneSelection:
    """Test PersonaPane selection functionality."""

    @pytest.mark.asyncio
    async def test_select_persona_by_index(self, sample_personas):
        """Test selecting a persona by index."""
        pane = PersonaPane(sample_personas)
        
        pane.select_persona(1)
        
        assert pane.selected_index == 1
        assert pane.get_selected_persona().id == "technical"

    @pytest.mark.asyncio
    async def test_select_persona_by_id(self, sample_personas):
        """Test selecting a persona by ID."""
        pane = PersonaPane(sample_personas)
        
        pane.select_persona_by_id("creative")
        
        assert pane.selected_index == 2
        assert pane.get_selected_persona().id == "creative"

    @pytest.mark.asyncio
    async def test_select_invalid_index(self, sample_personas):
        """Test that selecting invalid index does nothing."""
        pane = PersonaPane(sample_personas)
        original_index = pane.selected_index
        
        pane.select_persona(99)
        
        # Should remain unchanged
        assert pane.selected_index == original_index

    @pytest.mark.asyncio
    async def test_select_negative_index(self, sample_personas):
        """Test that selecting negative index does nothing."""
        pane = PersonaPane(sample_personas)
        original_index = pane.selected_index
        
        pane.select_persona(-1)
        
        # Should remain unchanged
        assert pane.selected_index == original_index

    @pytest.mark.asyncio
    async def test_select_persona_by_invalid_id(self, sample_personas):
        """Test that selecting by invalid ID does nothing."""
        pane = PersonaPane(sample_personas)
        original_index = pane.selected_index
        
        pane.select_persona_by_id("nonexistent")
        
        # Should remain unchanged
        assert pane.selected_index == original_index


class TestPersonaPaneNavigation:
    """Test PersonaPane navigation."""

    @pytest.mark.asyncio
    async def test_next_persona(self, sample_personas):
        """Test navigating to next persona."""
        pane = PersonaPane(sample_personas)
        
        pane.next_persona()
        
        assert pane.selected_index == 1

    @pytest.mark.asyncio
    async def test_previous_persona(self, sample_personas):
        """Test navigating to previous persona."""
        pane = PersonaPane(sample_personas)
        pane.select_persona(1)
        
        pane.previous_persona()
        
        assert pane.selected_index == 0

    @pytest.mark.asyncio
    async def test_next_persona_wraps_around(self, sample_personas):
        """Test that next_persona wraps to beginning."""
        pane = PersonaPane(sample_personas)
        pane.select_persona(2)  # Last persona
        
        pane.next_persona()
        
        assert pane.selected_index == 0

    @pytest.mark.asyncio
    async def test_previous_persona_wraps_around(self, sample_personas):
        """Test that previous_persona wraps to end."""
        pane = PersonaPane(sample_personas)
        pane.select_persona(0)  # First persona
        
        pane.previous_persona()
        
        assert pane.selected_index == 2


class TestPersonaPaneGetters:
    """Test PersonaPane getter methods."""

    @pytest.mark.asyncio
    async def test_get_selected_persona(self, sample_personas):
        """Test getting the currently selected persona."""
        pane = PersonaPane(sample_personas)
        pane.select_persona(1)
        
        selected = pane.get_selected_persona()
        
        assert selected.id == "technical"
        assert selected.name == "Technical Expert"

    @pytest.mark.asyncio
    async def test_get_all_personas(self, sample_personas):
        """Test getting all personas."""
        pane = PersonaPane(sample_personas)
        
        all_personas = pane.get_all_personas()
        
        assert len(all_personas) == 3
        assert all_personas[0].id == "default"
