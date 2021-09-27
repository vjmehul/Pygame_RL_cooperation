#Game parameters
inputshape=(84, 84, 4)

# model parameters
lr = 0.0001
eps_max=1.0
eps_min=0.01
eps_decay=0.9999998

#counters
env_steps_before_train = 30  # number of steps to skip before we train the model  # Frequency of Training the model # 10
steps_since_train=0          # Counter to find how many steps has been passed before the last ORIGINAL model update
tgt_model_update = 100       # target model update frequency  # recommended for env = 100
epochs_since_tgt = 0   # Counter to find how many steps has been passed before the last TARGET model update

#Test frequency
epochs_before_test = 200000  # frequency for testing the model # recoom. 100000

#Save frequency
Save_frequency = 500000

#replay memory parameters
replay_size=50000    #10000
sample_size=512    #64
