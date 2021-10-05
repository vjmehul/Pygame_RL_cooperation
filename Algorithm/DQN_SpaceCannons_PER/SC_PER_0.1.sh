#!/bin/bash
#SBATCH -N 1
#SBATCH -t 5-00:00:00
#SBATCH -p gpu_shared
export DISPLAY=:1
Xvfb $DISPLAY -auth /dev/null &
module load 2020
module load Python/3.8.2-GCCcore-9.3.0


#pip install -r /home/mverma/rl_cooperation/Pygame_RL_cooperation/Algorithm/requirements.txt
#echo "package loaded"
#python -m wandb login bb8b6304bd0410f5b77c36892ad419b65bafc0cb
#echo "wandb login complete"
cd /home/mverma/rl_cooperation/Pygame_RL_cooperation/SpaceCannons
echo "cd move complete"
pip install -e .
cd /home/mverma/rl_cooperation/Pygame_RL_cooperation/Algorithm/DQN_SpaceCannons_PER
#pip install moviepy imageio

python agent.py > out.txt

