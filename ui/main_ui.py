# ui/main_ui.py
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static, Header, Footer
from src.models import Gang
from src.rules import Rules
from src.scenario import Scenario
from rich.table import Table

class ScenarioUI(App):
    """A Textual App to visualize scenario progress."""

    def __init__(self, scenario: Scenario, **kwargs):
        super().__init__(**kwargs)
        self.scenario = scenario
        self.turn = 0

    def compose(self) -> ComposeResult:
        yield Header()
        self.panel = Static("", id="main_panel")
        yield self.panel
        yield Footer()

    def on_mount(self):
        # Start scenario or show initial state
        self.update_display()

    def update_display(self):
        # Create a table showing gangs status
        table = Table("Gang", "Alive Fighters", "Resources", title=f"Turn {self.turn}")
        for g in self.scenario.gangs:
            table.add_row(g.name, str(g.alive_fighters()), str(g.resources))
        self.panel.update(table)

    async def on_key(self, event):
        # Press 'n' to advance a turn (for example)
        if event.key == "n":
            self.turn += 1
            if self.turn <= self.scenario.num_turns and not self.scenario.end_condition_met():
                self.scenario_step()
            else:
                # scenario ended
                self.panel.update("Scenario ended!")

    def scenario_step(self):
        # Run one turn step manually
        # We need a modified Scenario that can run step-by-step rather than all at once.
        # For now, let's just call the internal scenario logic for a single turn.
        self.scenario_turn()
        self.update_display()

    def scenario_turn(self):
        # Extract the logic from scenario.run() into smaller steps so we can call them here.
        self.scenario.collect_resources()
        self.scenario.maintenance_phase()
        self.scenario.combat_phase()
        # no logging here, just the UI update. Check end conditions.
