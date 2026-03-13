# Directive: Auto-Potion System

## Objective
Automatically use life and mana potions based on character health/mana percentages.

## Parameters
- **HP Threshold**: 50% (Default)
- **Mana Threshold**: 30% (Default)
- **Life Potion Key**: `1`
- **Mana Potion Key**: `5`
- **Check Frequency**: 100ms

## Layer 3 Tools
- `execution/monitor_stats.py`: Monitors the character's status.
- `execution/potion_controls.py`: Executes the potion usage.

## Logic Flow
1. Identify the screen coordinates of the HP and Mana globes.
2. Read the pixel value at specific vertical levels of the globes to determine percentage.
3. If current HP < Threshold, trigger `potion_controls.py` for Life.
4. If current Mana < Threshold, trigger `potion_controls.py` for Mana.
5. Wait for the Check Frequency.
6. Repeat.

## Edge Cases
- **Full Transparency**: If the UI is hidden, the bot should stop or warn.
- **Loading Screens**: Bot should detect if it's in a loading screen to avoid wasting potions.
- **Lag**: Potion usage should have a cooldown to prevent spamming while the server lag updates the HP bar.
