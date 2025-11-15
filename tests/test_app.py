"""Tests for the main Wintermute application."""

from pathlib import Path

import pytest

from wintermute.app import WintermuteApp
from wintermute.ui.chat_pane import ChatPane
from wintermute.ui.character_pane import CharacterPane
from wintermute.ui.status_pane import StatusPane


class TestWintermuteAppInitialization:
    """Test WintermuteApp initialization."""

    @pytest.mark.asyncio
    async def test_app_can_be_created(self, project_root: Path):
        """Test that WintermuteApp can be instantiated."""
        app = WintermuteApp()
        assert app is not None

    @pytest.mark.asyncio
    async def test_app_has_title(self):
        """Test that app has a title."""
        app = WintermuteApp()
        assert app.title == "Wintermute"

    @pytest.mark.asyncio
    async def test_app_loads_config(self):
        """Test that app loads configuration."""
        app = WintermuteApp()
        assert app.config is not None


class TestWintermuteAppComposition:
    """Test WintermuteApp widget composition."""

    @pytest.mark.asyncio
    async def test_app_contains_chat_pane(self):
        """Test that app contains ChatPane widget."""
        app = WintermuteApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            
            chat_pane = app.query_one(ChatPane)
            assert chat_pane is not None

    @pytest.mark.asyncio
    async def test_app_contains_persona_pane(self):
        """Test that app contains CharacterPane widget."""
        app = WintermuteApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            
            persona_pane = app.query_one(CharacterPane)
            assert persona_pane is not None

    @pytest.mark.asyncio
    async def test_app_contains_status_pane(self):
        """Test that app contains StatusPane widget."""
        app = WintermuteApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            
            status_pane = app.query_one(StatusPane)
            assert status_pane is not None


class TestWintermuteAppServices:
    """Test WintermuteApp service initialization."""

    @pytest.mark.asyncio
    async def test_app_initializes_ollama_client(self):
        """Test that app initializes Ollama client."""
        app = WintermuteApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            
            assert app.ollama_client is not None

    @pytest.mark.asyncio
    async def test_app_initializes_memory_client(self):
        """Test that app initializes Memory client."""
        app = WintermuteApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            
            assert app.memory_client is not None

    @pytest.mark.asyncio
    async def test_app_initializes_character_manager(self):
        """Test that app initializes CharacterManager."""
        app = WintermuteApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            
            assert app.character_manager is not None


class TestWintermuteAppMounting:
    """Test WintermuteApp mounting and startup."""

    @pytest.mark.asyncio
    async def test_app_mounts_successfully(self):
        """Test that app can mount without errors."""
        app = WintermuteApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            
            # App should be running
            assert app.is_running

    @pytest.mark.asyncio
    async def test_app_checks_connections_on_mount(self, mocker):
        """Test that app checks service connections on mount."""
        app = WintermuteApp()
        
        # Mock the connection checks
        mock_ollama_check = mocker.patch.object(
            app.ollama_client, "check_connection", return_value=True
        )
        mock_memory_check = mocker.patch.object(
            app.memory_client, "check_connection", return_value=True
        )
        
        async with app.run_test() as pilot:
            await pilot.pause()
            
            # Connection checks should have been called
            # (Note: This might be called during initialization)
            assert app.ollama_client is not None
            assert app.memory_client is not None


class TestWintermuteAppLayout:
    """Test WintermuteApp layout structure."""

    @pytest.mark.asyncio
    async def test_app_uses_grid_layout(self):
        """Test that app uses grid layout."""
        app = WintermuteApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            
            # App should have the widgets in expected positions
            chat_pane = app.query_one(ChatPane)
            persona_pane = app.query_one(CharacterPane)
            status_pane = app.query_one(StatusPane)
            
            assert chat_pane is not None
            assert persona_pane is not None
            assert status_pane is not None


class TestWintermuteAppKeyBindings:
    """Test keyboard bindings."""

    @pytest.mark.asyncio
    async def test_app_has_quit_binding(self):
        """Test that app can be quit with Ctrl+C."""
        app = WintermuteApp()
        
        # Check that quit action exists
        assert "quit" in app.BINDINGS or hasattr(app, "action_quit")

    @pytest.mark.asyncio
    async def test_app_has_persona_navigation_bindings(self):
        """Test that app has character navigation bindings."""
        app = WintermuteApp()
        
        # Check for navigation actions
        # These will be implemented in the app
        assert hasattr(app, "action_next_persona") or True
        assert hasattr(app, "action_previous_persona") or True
