#Game parameters
inputshape=(84, 84, 4)

# model parameters
lr = 0.0001
eps_max=1.0
eps_min=0.01
eps_decay=0.9999975

#counters
env_steps_before_train = 5  # number of steps to skip before we train the model  # Frequency of Training the model # 10
steps_since_train=0          # Counter to find how many steps has been passed before the last ORIGINAL model update
tgt_model_update = 1000       # target model update frequency  # recommended for env = 1000
epochs_since_tgt = 0   # Counter to find how many steps has been passed before the last TARGET model update

#Test frequency
epochs_before_test = 50  # frequency for testing the model # recoom. 100000

#Save frequency
Save_frequency = 5000

#replay memory parameters
replay_size=200    #10000
sample_size=32    #64
