import logging
from gym.envs.registration import register

logger = logging.getLogger(__name__)

register(
    id='SpaceCannon-v0',
    entry_point='Space_cannons.envs:custom_game_env',
)
