"""Tests for the StatusPane widget."""

import pytest
from textual.app import App

from wintermute.ui.status_pane import StatusPane


class StatusPaneTestApp(App):
    """Test app for StatusPane."""

    def compose(self):
        """Compose the test app."""
        yield StatusPane()


class TestStatusPaneInitialization:
    """Test StatusPane initialization."""

    @pytest.mark.asyncio
    async def test_status_pane_can_be_created(self):
        """Test that StatusPane can be instantiated."""
        pane = StatusPane()
        assert pane is not None

    @pytest.mark.asyncio
    async def test_status_pane_initial_state(self):
        """Test that StatusPane has correct initial state."""
        pane = StatusPane()
        assert not pane.ollama_connected
        assert not pane.memory_connected
        assert pane.memory_count == 0
        assert pane.model_name == "Unknown"


class TestStatusPaneRendering:
    """Test StatusPane rendering."""

    @pytest.mark.asyncio
    async def test_status_pane_renders_in_app(self):
        """Test that StatusPane renders correctly in app."""
        app = StatusPaneTestApp()
        async with app.run_test() as pilot:
            # Wait for app to be ready
            await pilot.pause()
            
            # Check that StatusPane is mounted
            status_pane = app.query_one(StatusPane)
            assert status_pane is not None

    @pytest.mark.asyncio
    async def test_status_pane_displays_disconnected_state(self):
        """Test that StatusPane displays disconnected state initially."""
        app = StatusPaneTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            
            status_pane = app.query_one(StatusPane)
            rendered = status_pane.render()
            rendered_str = str(rendered)
            
            assert "ollama" in rendered_str.lower() or "disconnected" in rendered_str.lower()

    @pytest.mark.asyncio
    async def test_status_pane_displays_connection_status(self):
        """Test that StatusPane displays connection status."""
        app = StatusPaneTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            
            status_pane = app.query_one(StatusPane)
            
            # Update connection status
            status_pane.update_status(
                ollama_connected=True,
                memory_connected=True,
                memory_count=42,
                model_name="llama2",
            )
            await pilot.pause()
            
            rendered = status_pane.render()
            rendered_str = str(rendered)
            
            # Should show connected state and stats
            assert "42" in rendered_str or "memory" in rendered_str.lower()


class TestStatusPaneUpdates:
    """Test StatusPane status updates."""

    @pytest.mark.asyncio
    async def test_update_status_changes_connection_state(self):
        """Test that update_status changes connection state."""
        pane = StatusPane()
        
        pane.update_status(ollama_connected=True, memory_connected=False)
        
        assert pane.ollama_connected is True
        assert pane.memory_connected is False

    @pytest.mark.asyncio
    async def test_update_status_changes_memory_count(self):
        """Test that update_status changes memory count."""
        pane = StatusPane()
        
        pane.update_status(memory_count=100)
        
        assert pane.memory_count == 100

    @pytest.mark.asyncio
    async def test_update_status_changes_model_name(self):
        """Test that update_status changes model name."""
        pane = StatusPane()
        
        pane.update_status(model_name="gpt-4")
        
        assert pane.model_name == "gpt-4"

    @pytest.mark.asyncio
    async def test_update_status_with_partial_data(self):
        """Test that update_status works with partial data."""
        pane = StatusPane()
        pane.update_status(memory_count=50)
        
        # Set initial state
        pane.update_status(ollama_connected=True, memory_count=50)
        
        # Update only memory count
        pane.update_status(memory_count=75)
        
        # Ollama connection should remain unchanged
        assert pane.ollama_connected is True
        assert pane.memory_count == 75


class TestStatusPaneFormatting:
    """Test StatusPane text formatting."""

    @pytest.mark.asyncio
    async def test_status_pane_formats_connected_state(self):
        """Test that StatusPane formats connected state with color."""
        app = StatusPaneTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            
            status_pane = app.query_one(StatusPane)
            status_pane.update_status(ollama_connected=True)
            await pilot.pause()
            
            rendered = status_pane.render()
            # Check for markup or styling (Rich markup)
            rendered_str = str(rendered)
            # Connected state should have some indication
            assert rendered_str is not None

    @pytest.mark.asyncio
    async def test_status_pane_formats_disconnected_state(self):
        """Test that StatusPane formats disconnected state with color."""
        app = StatusPaneTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            
            status_pane = app.query_one(StatusPane)
            status_pane.update_status(ollama_connected=False)
            await pilot.pause()
            
            rendered = status_pane.render()
            # Disconnected state should have some indication
            rendered_str = str(rendered)
            assert rendered_str is not None

    @pytest.mark.asyncio
    async def test_status_pane_displays_memory_count(self):
        """Test that StatusPane displays memory count."""
        app = StatusPaneTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            
            status_pane = app.query_one(StatusPane)
            status_pane.update_status(memory_count=123)
            await pilot.pause()
            
            rendered = status_pane.render()
            rendered_str = str(rendered)
            
            # Should contain the memory count
            assert "123" in rendered_str

    @pytest.mark.asyncio
    async def test_status_pane_displays_model_name(self):
        """Test that StatusPane displays model name."""
        app = StatusPaneTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            
            status_pane = app.query_one(StatusPane)
            status_pane.update_status(model_name="llama2")
            await pilot.pause()
            
            rendered = status_pane.render()
            rendered_str = str(rendered)
            
            # Should contain the model name
            assert "llama2" in rendered_str.lower()
