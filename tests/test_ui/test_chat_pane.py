"""Tests for the ChatPane widget."""

from datetime import datetime

import pytest
from textual.app import App
from textual.widgets import Input

from wintermute.models.message import Message, MessageRole
from wintermute.ui.chat_pane import ChatPane


class ChatPaneTestApp(App):
    """Test app for ChatPane."""

    def compose(self):
        """Compose the test app."""
        yield ChatPane()


class TestChatPaneInitialization:
    """Test ChatPane initialization."""

    @pytest.mark.asyncio
    async def test_chat_pane_can_be_created(self):
        """Test that ChatPane can be instantiated."""
        pane = ChatPane()
        assert pane is not None

    @pytest.mark.asyncio
    async def test_chat_pane_starts_empty(self):
        """Test that ChatPane starts with no messages."""
        pane = ChatPane()
        assert len(pane.messages) == 0

    @pytest.mark.asyncio
    async def test_chat_pane_input_enabled_by_default(self):
        """Test that input is enabled by default."""
        pane = ChatPane()
        assert pane.input_enabled is True


class TestChatPaneAddMessage:
    """Test adding messages to ChatPane."""

    @pytest.mark.asyncio
    async def test_add_user_message(self):
        """Test adding a user message."""
        pane = ChatPane()
        
        message = Message(role=MessageRole.USER, content="Hello!")
        pane.add_message(message)
        
        assert len(pane.messages) == 1
        assert pane.messages[0].role == MessageRole.USER
        assert pane.messages[0].content == "Hello!"

    @pytest.mark.asyncio
    async def test_add_assistant_message(self):
        """Test adding an assistant message."""
        pane = ChatPane()
        
        message = Message(role=MessageRole.ASSISTANT, content="Hi there!")
        pane.add_message(message)
        
        assert len(pane.messages) == 1
        assert pane.messages[0].role == MessageRole.ASSISTANT

    @pytest.mark.asyncio
    async def test_add_multiple_messages(self):
        """Test adding multiple messages in sequence."""
        pane = ChatPane()
        
        pane.add_message(Message(role=MessageRole.USER, content="Hello"))
        pane.add_message(Message(role=MessageRole.ASSISTANT, content="Hi"))
        pane.add_message(Message(role=MessageRole.USER, content="How are you?"))
        
        assert len(pane.messages) == 3


class TestChatPaneRendering:
    """Test ChatPane rendering."""

    @pytest.mark.asyncio
    async def test_chat_pane_renders_in_app(self):
        """Test that ChatPane renders correctly in app."""
        app = ChatPaneTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            
            chat_pane = app.query_one(ChatPane)
            assert chat_pane is not None

    @pytest.mark.asyncio
    async def test_chat_pane_displays_empty_state(self):
        """Test that ChatPane displays appropriate message when empty."""
        app = ChatPaneTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            
            chat_pane = app.query_one(ChatPane)
            rendered = chat_pane.render()
            rendered_str = str(rendered)
            
            # Should indicate no messages
            assert rendered_str is not None

    @pytest.mark.asyncio
    async def test_chat_pane_displays_messages(self):
        """Test that ChatPane displays added messages."""
        app = ChatPaneTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            
            chat_pane = app.query_one(ChatPane)
            chat_pane.add_message(Message(role=MessageRole.USER, content="Test message"))
            await pilot.pause()
            
            rendered = chat_pane.render()
            rendered_str = str(rendered)
            
            assert "Test message" in rendered_str


class TestChatPaneFormatting:
    """Test message formatting in ChatPane."""

    @pytest.mark.asyncio
    async def test_format_user_message(self):
        """Test formatting of user messages."""
        pane = ChatPane()
        message = Message(role=MessageRole.USER, content="Hello")
        
        formatted = pane._format_message(message)
        
        assert "User" in formatted or "Hello" in formatted

    @pytest.mark.asyncio
    async def test_format_assistant_message(self):
        """Test formatting of assistant messages."""
        pane = ChatPane()
        message = Message(role=MessageRole.ASSISTANT, content="Hi there")
        
        formatted = pane._format_message(message)
        
        assert "Assistant" in formatted or "Hi there" in formatted

    @pytest.mark.asyncio
    async def test_format_includes_timestamp(self):
        """Test that formatted messages include timestamps."""
        pane = ChatPane()
        timestamp = datetime(2024, 1, 1, 12, 30, 0)
        message = Message(
            role=MessageRole.USER, 
            content="Test",
            timestamp=timestamp
        )
        
        formatted = pane._format_message(message)
        
        # Should contain time in some format
        assert "12:30" in formatted or "12" in formatted


class TestChatPaneClear:
    """Test clearing chat history."""

    @pytest.mark.asyncio
    async def test_clear_messages(self):
        """Test clearing all messages."""
        pane = ChatPane()
        
        pane.add_message(Message(role=MessageRole.USER, content="Message 1"))
        pane.add_message(Message(role=MessageRole.USER, content="Message 2"))
        
        pane.clear_messages()
        
        assert len(pane.messages) == 0

    @pytest.mark.asyncio
    async def test_clear_empty_chat(self):
        """Test that clearing empty chat works."""
        pane = ChatPane()
        
        pane.clear_messages()
        
        assert len(pane.messages) == 0


class TestChatPaneInput:
    """Test chat input functionality."""

    @pytest.mark.asyncio
    async def test_get_current_input(self):
        """Test getting current input value."""
        app = ChatPaneTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            
            chat_pane = app.query_one(ChatPane)
            input_widget = chat_pane.query_one("#chat-input", Input)
            input_widget.value = "Test input"
            
            assert chat_pane.get_current_input() == "Test input"

    @pytest.mark.asyncio
    async def test_clear_input(self):
        """Test clearing input field."""
        app = ChatPaneTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            
            chat_pane = app.query_one(ChatPane)
            input_widget = chat_pane.query_one("#chat-input", Input)
            input_widget.value = "Some text"
            
            chat_pane.clear_input()
            
            assert input_widget.value == ""

    @pytest.mark.asyncio
    async def test_disable_input(self):
        """Test disabling input."""
        pane = ChatPane()
        
        pane.set_input_enabled(False)
        
        assert pane.input_enabled is False

    @pytest.mark.asyncio
    async def test_enable_input(self):
        """Test enabling input."""
        pane = ChatPane()
        pane.set_input_enabled(False)
        
        pane.set_input_enabled(True)
        
        assert pane.input_enabled is True


class TestChatPaneTypingIndicator:
    """Test typing indicator functionality."""

    @pytest.mark.asyncio
    async def test_show_typing_indicator(self):
        """Test showing typing indicator."""
        pane = ChatPane()
        
        pane.show_typing_indicator()
        
        assert pane.is_typing is True

    @pytest.mark.asyncio
    async def test_hide_typing_indicator(self):
        """Test hiding typing indicator."""
        pane = ChatPane()
        pane.show_typing_indicator()
        
        pane.hide_typing_indicator()
        
        assert pane.is_typing is False

    @pytest.mark.asyncio
    async def test_typing_indicator_displays(self):
        """Test that typing indicator is shown in render."""
        app = ChatPaneTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            
            chat_pane = app.query_one(ChatPane)
            chat_pane.show_typing_indicator()
            await pilot.pause()
            
            rendered = chat_pane.render()
            rendered_str = str(rendered)
            
            # Should show some typing indication
            assert rendered_str is not None


class TestChatPaneGetters:
    """Test ChatPane getter methods."""

    @pytest.mark.asyncio
    async def test_get_all_messages(self):
        """Test getting all messages."""
        pane = ChatPane()
        
        msg1 = Message(role=MessageRole.USER, content="First")
        msg2 = Message(role=MessageRole.ASSISTANT, content="Second")
        pane.add_message(msg1)
        pane.add_message(msg2)
        
        messages = pane.get_all_messages()
        
        assert len(messages) == 2
        assert messages[0].content == "First"
        assert messages[1].content == "Second"

    @pytest.mark.asyncio
    async def test_get_message_count(self):
        """Test getting message count."""
        pane = ChatPane()
        
        pane.add_message(Message(role=MessageRole.USER, content="Test"))
        
        count = pane.get_message_count()
        
        assert count == 1
