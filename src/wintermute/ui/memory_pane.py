"""Memory pane widget for displaying recent memories."""

from datetime import datetime
from typing import Optional

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget


class MemoryPane(Widget):
    """Widget displaying recent memories for the active character."""

    # Reactive properties
    memories: reactive[list[dict]] = reactive(list, always_update=True)
    character_name: reactive[str] = reactive("Unknown")

    def update_memories(
        self,
        memories: list[dict],
        character_name: str,
    ) -> None:
        """
        Update the displayed memories.

        Args:
            memories: List of memory objects from OpenMemory.
            character_name: Name of the character these memories belong to.
        """
        self.memories = memories
        self.character_name = character_name

    def render(self) -> Text:
        """
        Render the memory display.

        Returns:
            Rich Text object with formatted memory information.
        """
        text = Text()

        # Title
        text.append(f"Recent Memories ({self.character_name})\n", style="bold underline")
        text.append("\n")

        if not self.memories:
            text.append("No memories yet\n", style="dim italic")
            text.append("Start chatting to build memories!\n", style="dim")
            return text

        # Display recent memories (limit to 5 for display)
        display_memories = self.memories[:5]
        
        for memory in display_memories:
            content = memory.get("content", "")
            
            # Truncate long content
            if len(content) > 60:
                content = content[:57] + "..."
            
            # Show timestamp if available
            timestamp = memory.get("last_seen_at")
            if timestamp:
                # Convert milliseconds to datetime
                dt = datetime.fromtimestamp(timestamp / 1000)
                time_str = dt.strftime("%H:%M")
                text.append(f"[{time_str}] ", style="dim")
            
            # Show content
            text.append(f"{content}\n", style="white")
            
            # Show tags if available
            tags = memory.get("tags", [])
            if tags:
                text.append(f"  Tags: {', '.join(tags)}\n", style="dim cyan")
            
            # Show score/salience
            salience = memory.get("salience", 0)
            text.append(f"  Salience: {salience:.2f}\n", style="dim yellow")
            
            text.append("\n")

        # Show summary
        total_count = len(self.memories)
        shown_count = len(display_memories)
        text.append(f"Showing {shown_count} of {total_count} memories\n", style="dim italic")

        return text
