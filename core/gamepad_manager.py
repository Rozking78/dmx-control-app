"""
Gamepad Manager - Handle gamepad input with configurable mappings
"""

import json
import os
from typing import Optional, Dict, Any, Callable
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


class GamepadWorker(QThread):
    """Worker thread for polling gamepad input."""

    button_pressed = pyqtSignal(int)  # Button index
    button_released = pyqtSignal(int)
    axis_moved = pyqtSignal(int, float)  # Axis index, value
    connected = pyqtSignal(str)  # Gamepad name
    disconnected = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.running = False
        self.joystick = None
        self.last_button_states = {}
        self.last_hat_state = (0, 0)
        self.deadzone = 0.2

    def run(self):
        """Main polling loop."""
        if not PYGAME_AVAILABLE:
            return

        pygame.init()
        pygame.joystick.init()

        self.running = True

        while self.running:
            pygame.event.pump()

            # Check for joystick connection
            joystick_count = pygame.joystick.get_count()

            if joystick_count > 0 and self.joystick is None:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                self.connected.emit(self.joystick.get_name())

            elif joystick_count == 0 and self.joystick is not None:
                self.joystick = None
                self.disconnected.emit()

            # Poll input if connected
            if self.joystick:
                # Buttons
                for i in range(self.joystick.get_numbuttons()):
                    pressed = self.joystick.get_button(i)
                    was_pressed = self.last_button_states.get(i, False)

                    if pressed and not was_pressed:
                        self.button_pressed.emit(i)
                    elif not pressed and was_pressed:
                        self.button_released.emit(i)

                    self.last_button_states[i] = pressed

                # Axes
                for i in range(self.joystick.get_numaxes()):
                    value = self.joystick.get_axis(i)
                    if abs(value) > self.deadzone:
                        self.axis_moved.emit(i, value)

                # D-Pad (hat) - convert to button events
                for i in range(self.joystick.get_numhats()):
                    hat = self.joystick.get_hat(i)
                    # hat = (x, y) where x: -1=left, 1=right, y: -1=down, 1=up

                    # Map hat directions to virtual button indices
                    # 12=up, 13=down, 14=left, 15=right
                    hat_buttons = {
                        (0, 1): 12,   # Up
                        (0, -1): 13,  # Down
                        (-1, 0): 14,  # Left
                        (1, 0): 15,   # Right
                        (1, 1): 12,   # Up-Right (emit up)
                        (-1, 1): 12,  # Up-Left (emit up)
                        (1, -1): 13,  # Down-Right (emit down)
                        (-1, -1): 13, # Down-Left (emit down)
                    }

                    # Check if hat state changed
                    if hat != self.last_hat_state:
                        # Release old direction
                        if self.last_hat_state in hat_buttons:
                            self.button_released.emit(hat_buttons[self.last_hat_state])

                        # Press new direction
                        if hat in hat_buttons:
                            self.button_pressed.emit(hat_buttons[hat])

                        self.last_hat_state = hat

            self.msleep(16)  # ~60 Hz polling

        pygame.quit()

    def stop(self):
        """Stop the worker thread."""
        self.running = False
        self.wait()


class GamepadManager(QObject):
    """Manages gamepad input and button mappings."""

    button_pressed = pyqtSignal(int, str)  # Button index, action name
    axis_moved = pyqtSignal(str, float)  # Axis name, value
    gamepad_connected = pyqtSignal(str)  # Gamepad name
    gamepad_disconnected = pyqtSignal()

    # Default button mappings (Steam Deck / Xbox layout)
    DEFAULT_MAPPINGS = {
        0: 'select',      # A
        1: 'back',        # B
        2: 'refresh',     # X
        3: 'context',     # Y
        4: 'prev_tab',    # LB
        5: 'next_tab',    # RB
        6: 'modifier',    # LT (as button)
        7: 'none',        # RT (as button)
        8: 'reset',       # Select/Back
        9: 'save',        # Start
        10: 'none',       # L3
        11: 'none',       # R3
        12: 'nav_up',     # D-Pad Up
        13: 'nav_down',   # D-Pad Down
        14: 'nav_left',   # D-Pad Left
        15: 'nav_right',  # D-Pad Right
    }

    def __init__(self, config_manager=None):
        super().__init__()
        self.config = config_manager
        self.worker = None
        self.connected = False
        self.gamepad_name = None

        # Load mappings
        self.mappings = dict(self.DEFAULT_MAPPINGS)
        self.analog_settings = {
            'deadzone': 0.2,
            'sensitivity': 1.0,
            'invert_y': False,
        }

        self.load_profile()

    def start(self):
        """Start listening for gamepad input."""
        if not PYGAME_AVAILABLE:
            print("Warning: pygame not available, gamepad support disabled")
            return

        self.worker = GamepadWorker()
        self.worker.button_pressed.connect(self._on_button_pressed)
        self.worker.button_released.connect(self._on_button_released)
        self.worker.axis_moved.connect(self._on_axis_moved)
        self.worker.connected.connect(self._on_connected)
        self.worker.disconnected.connect(self._on_disconnected)
        self.worker.start()

    def stop(self):
        """Stop listening for gamepad input."""
        if self.worker:
            self.worker.stop()
            self.worker = None

    def _on_button_pressed(self, button_index: int):
        """Handle raw button press."""
        action = self.mappings.get(button_index, 'none')
        if action != 'none':
            self.button_pressed.emit(button_index, action)

    def _on_button_released(self, button_index: int):
        """Handle raw button release."""
        pass  # Could emit release events if needed

    def _on_axis_moved(self, axis_index: int, value: float):
        """Handle axis movement."""
        # Apply sensitivity
        value *= self.analog_settings['sensitivity']

        # Invert Y if configured (axes 1 and 3 are typically Y axes)
        if self.analog_settings['invert_y'] and axis_index in (1, 3):
            value = -value

        axis_names = {0: 'left_x', 1: 'left_y', 2: 'right_x', 3: 'right_y'}
        axis_name = axis_names.get(axis_index, f'axis_{axis_index}')
        self.axis_moved.emit(axis_name, value)

    def _on_connected(self, name: str):
        """Handle gamepad connection."""
        self.connected = True
        self.gamepad_name = name
        self.gamepad_connected.emit(name)

    def _on_disconnected(self):
        """Handle gamepad disconnection."""
        self.connected = False
        self.gamepad_name = None
        self.gamepad_disconnected.emit()

    def set_mapping(self, button_index: int, action: str):
        """Set a button mapping."""
        self.mappings[button_index] = action

    def get_mapping(self, button_index: int) -> str:
        """Get the action for a button."""
        return self.mappings.get(button_index, 'none')

    def set_deadzone(self, value: float):
        """Set analog deadzone."""
        self.analog_settings['deadzone'] = max(0.0, min(0.5, value))
        if self.worker:
            self.worker.deadzone = self.analog_settings['deadzone']

    def set_sensitivity(self, value: float):
        """Set analog sensitivity."""
        self.analog_settings['sensitivity'] = max(0.5, min(2.0, value))

    def set_invert_y(self, invert: bool):
        """Set Y axis inversion."""
        self.analog_settings['invert_y'] = invert

    def reset_to_defaults(self):
        """Reset mappings to defaults."""
        self.mappings = dict(self.DEFAULT_MAPPINGS)
        self.analog_settings = {
            'deadzone': 0.2,
            'sensitivity': 1.0,
            'invert_y': False,
        }

    def load_profile(self, name: str = None):
        """Load a gamepad profile."""
        if self.config:
            profile = self.config.get_gamepad_profile(name)
            if profile:
                self.mappings = profile.get('buttons', dict(self.DEFAULT_MAPPINGS))
                self.analog_settings = profile.get('analog', self.analog_settings)

    def save_profile(self, name: str):
        """Save current settings as a profile."""
        if self.config:
            profile = {
                'name': name,
                'buttons': self.mappings,
                'analog': self.analog_settings,
            }
            self.config.save_gamepad_profile(name, profile)

    def get_profile_data(self) -> Dict[str, Any]:
        """Get current profile data."""
        return {
            'buttons': dict(self.mappings),
            'analog': dict(self.analog_settings),
        }

    def is_connected(self) -> bool:
        """Check if a gamepad is connected."""
        return self.connected

    def get_gamepad_name(self) -> Optional[str]:
        """Get the connected gamepad name."""
        return self.gamepad_name


# Action definitions for the UI
AVAILABLE_ACTIONS = {
    'select': 'Select/Confirm',
    'back': 'Back/Cancel',
    'refresh': 'Refresh',
    'context': 'Context Action',
    'prev_tab': 'Previous Tab',
    'next_tab': 'Next Tab',
    'save': 'Save/Apply',
    'reset': 'Reset',
    'nav_up': 'Navigate Up',
    'nav_down': 'Navigate Down',
    'nav_left': 'Navigate Left',
    'nav_right': 'Navigate Right',
    'modifier': 'Fine Control',
    'none': 'Not Assigned',
}

BUTTON_NAMES = {
    0: 'A',
    1: 'B',
    2: 'X',
    3: 'Y',
    4: 'LB',
    5: 'RB',
    6: 'LT',
    7: 'RT',
    8: 'Select',
    9: 'Start',
    10: 'L3',
    11: 'R3',
    12: 'D-Up',
    13: 'D-Down',
    14: 'D-Left',
    15: 'D-Right',
}
