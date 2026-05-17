from __future__ import annotations

from .adapters.displayhatmini_adapter import DisplayHatMiniAdapter
from .main import handle_actions
from .router import ScreenRouter
from .state import DeviceState
from .ui import UI
from .config_manager import load_config, apply_runtime_config_to_state


def main() -> None:
    adapter = DisplayHatMiniAdapter(fps=20)
    ui = UI()
    state = DeviceState()
    apply_runtime_config_to_state(state, load_config())
    router = ScreenRouter(auto_cycle_seconds=9.0)

    try:
        while adapter.running:
            actions = adapter.poll()
            handle_actions(actions, state, router, adapter)

            state.tick()
            router.tick(state)

            adapter.clear()
            screen = router.current(state)
            screen.draw(adapter.logical, ui, state)
            adapter.set_led(state.led_color)
            adapter.present()
            adapter.fps()
    finally:
        adapter.close()


if __name__ == "__main__":
    main()
