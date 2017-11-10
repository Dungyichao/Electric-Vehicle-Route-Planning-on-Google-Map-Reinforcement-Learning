from Environment import environment
from DoubleDQN import Qnetwork
import numpy as np
import tensorflow as tf
import pandas as pd
import time as tm
from haversine import haversine
#import random
from random import sample
import math
# action is in the set of (0,1,2,3) = (north, east, south, west)
# s1, r, d = env.step(2)   # s1: next state = (lat,lng)  // r: reward for taking step  // d: End, True or False
#  initialize environment  env = environment('Purdue University West Lafayette', '40.3025301,-86.886558')
class experience_replay_buffer():
    def __init__(self, size = 50000):
        self.buffer = []
        self.buffersize = size
    def append(self, exp):
        if len(self.buffer) + len(exp) >= self.buffersize:
            self.buffer[0:len(self.buffer) + len(exp) - self.buffersize] = []
        self.buffer.extend(exp)
    def batch(self, num):
        return np.reshape(np.array(sample(self.buffer, num)),[num, 5])

def update_net(trainable_var, sess):
    num = len(trainable_var)
    container = []
    for id,var in enumerate(trainable_var[0:int(num/2)]):
        container.append(trainable_var[id+int(num/2)].assign(var))
    sess.run(container)
    
print("------------for tensorflow --------------")
tf.reset_default_graph()
with tf.variable_scope('Qnet'):
    Qnet = Qnetwork(s_size=2, a_size=4)
with tf.variable_scope('Targetnet'):
    Targetnet = Qnetwork(s_size=2, a_size=4)



print("------------for env & google info--------------")
env = environment('40.468254,-86.980963', '40.445283,-86.948429')
step_rewardG, chargenumG, SOCG, timeG = env.origine_map_reward()  # The info of google map route
env.battery_charge()
step_length = 1000  # meter
env.length = 1000 / step_length
print("stride length: ", env.length)
learning_rate = 0.0001
#sleep = False

print("------------for map --------------")
s = env.start_position
saver = tf.train.Saver(max_to_keep=50)
print("map bound: ", env.map_bound)
north = env.map_bound['north']
east = env.map_bound['east']
west = env.map_bound['west']
south = env.map_bound['south']
upper_left = (north, west)
upper_right = (north, east)
lower_left = (south, west)
lower_right = (south, east)
map_height = haversine(upper_left, lower_left)
map_wide = haversine(upper_left, upper_right) if haversine(upper_left, upper_right) > haversine(lower_left, lower_right) else haversine(lower_left, lower_right)
#print("map height stride: ", (north - south)/(map_height*env.length))
#print("map height (km): ", map_height)
#print("env.stride height(km): ", env.envheightkm)
#print("map wide(km): ", map_wide)
wide_grid_num = map_wide / (step_length/1000)    # the number of grid point
height_grid_num = map_height / (step_length/1000) 
total_point = int(math.ceil(wide_grid_num) * math.ceil(height_grid_num))
print("total grid point: ", total_point)
max_train_step = 4 * math.ceil(wide_grid_num) * math.ceil(height_grid_num)
print("Max trainning steps: ", max_train_step)
pre_train_step = max_train_step * 5
print("Pre train step: ", pre_train_step)
s_list = list(s)
print("start position: ", s_list)
print("end position: ", env.end_position)
replay_buffer = experience_replay_buffer()
init = tf.global_variables_initializer()
trainable_var = tf.trainable_variables()
print("trainable_var", len(trainable_var))



print("------------Parameter --------------")
path = "./ev/model"
pre_train = pre_train_step  # don't update and train the model within these steps
train_num = 10000   # total episode num
max_step = max_train_step
updata_f = 5   # frequency of copy weights from Qnet to Targetnet
batch_num = 32
gamma = 0.9 # discount factor
high_prob = 1
low_prob = 0.1
slope = (high_prob - low_prob) / 2000
############### Load Model
pathload = "./ev/Result/23_proceed/result6"
load_model = False
modelnum = 24
sleep = False
if load_model == True:
    high_prob = 0.5
############### initialize constant
tt = 0

print("------------Save training parameters--------------")
parameter = [env.map_bound, map_height, map_wide, step_length, wide_grid_num, height_grid_num, total_point, max_train_step, pre_train_step, learning_rate, step_rewardG, chargenumG, SOCG, timeG]
df_1 = pd.DataFrame([parameter])
df_1.to_csv("./ev/train_para.csv", header=["google map_boundary", "map_height(km)", "map_wide(km)", "step_length(m)", "wide_grid_num", "height_grid_num", "total_point", "max_train_step in episode", "pre_train_step", "learning_rate", "Google r", "Google charge num", "Google SOC", "Google time"])

print("sleep 5 min")
tm.sleep(10)
print("------------Start training --------------")
with tf.Session() as sess:
    sess.run(init)
    battery = []
    total_step = 0
    episode_num = 1
    reward_history = []
    e = high_prob
    if load_model == True:
        print("Loading Model....")
        saver.restore(sess, pathload+"/model-"+str(modelnum)+".ckpt")
        print("Model restored.")

    for episode in range(train_num):  # num of episode
        s = env.start_position
        s_list = list(s)
        env.battery_charge()
        ss, nn = env.battery_condition()
        print("Current Episode: ", episode_num)
        #print("SOC, charge_number: ",ss,nn)
        #print("S_list: ", s_list)
        print("current position: ", env.current_position)
        episode_num = episode_num + 1
        in_ep_step = 0
        step_buffer = []
        episode_reward = 0
        testt = [] # try
        random_a = 0
        network_a = 0
        avg_loss = 0
        overQ_num = 0 # OVER_QUERY_LIMIT
        unreach_step_history = []
        loss_history = []
        overQ_num_roll = 0
        while (in_ep_step <= max_step):   # Max step in one episode
            #step_buffer.append(s_list)
            test = 0 # try
            istrain = 0 # try
            isupdate = 0 # try
            Q_value = 0
            in_ep_loss = 0
            update_num = 0
            if np.random.rand(1) < e or (total_step < pre_train and load_model == False):
                action = np.random.randint(0,4)
                test = 1 # try
            else:
                action = sess.run(Qnet.predict, feed_dict={Qnet.input:[s_list]})[0]
                #action = float(actionn)
                Q_value = sess.run(Qnet.action, feed_dict={Qnet.input:[s_list]}) # for data analysis
                test = 2 # try
            #print(action)
	    # how to choose action 
            if test == 1:
                random_a = random_a + 1
            # how to choose action    
            if test == 2:
                network_a = network_a + 1
            # take the action and get s', r, status, chargenum, SOC
            s1, r, d, charge_num, SOC = env.step(action)  
            s = list(s1)
            #print(SOC)
            
            episode_reward = episode_reward + r
            if env.status_dir_check != 'OVER_QUERY_LIMIT':
                step_buffer.append([s_list, action, r, s, d])
                replay_buffer.append(np.reshape(np.array([s_list, action, r, s, d]),[1,5]))
                in_ep_step = in_ep_step + 1
                total_step = total_step + 1
                s_list = s
            if env.status_dir_check == 'OVER_QUERY_LIMIT':
                overQ_num = overQ_num + 1
                overQ_num_roll = overQ_num_roll + 1
             
            if (total_step > pre_train and env.status_dir_check != 'OVER_QUERY_LIMIT' and len(replay_buffer.buffer) > batch_num) or (load_model == True and len(replay_buffer.buffer) > batch_num):  # start updating model
                if e > low_prob:
                    e -= slope                     
                ex_batch = replay_buffer.batch(batch_num)
                Qnet_pre = sess.run(Qnet.predict, feed_dict={Qnet.input:np.vstack(ex_batch[:,3])})
                #print(Qnet_pre)
                Targetnet_action = sess.run(Targetnet.action, feed_dict={Targetnet.input:np.vstack(ex_batch[:,3])})
                #print(Targetnet_action)
                mul = 1 - ex_batch[:,4]   # 1 if d=False; 0 if d=True
                #print(mul)
                y = ex_batch[:,2] + mul * gamma * Targetnet_action[range(batch_num),Qnet_pre]  # target Q
                #print(y)
                #Q = sess.run(Targetnet.Q, feed_dict={Targetnet.input:np.vstack(ex_batch[:,3]), Targetnet.a:ex_batch[:,1]})
                #print(Q)
                #error = sess.run(Targetnet.error, feed_dict={Targetnet.input:np.vstack(ex_batch[:,3]),Targetnet.target_y:y, Targetnet.a:ex_batch[:,1]})
                #print(error)
                loss = sess.run(Qnet.loss, feed_dict={Qnet.input:np.vstack(ex_batch[:,0]),Qnet.target_y:y, Qnet.a:ex_batch[:,1]}) # We use Qnet loss to update Qnet
                in_ep_loss = in_ep_loss + loss
                if total_step % 10 == 0:
                    loss_history.append(loss)
                #print(loss)
                # update model
                _ = sess.run(Qnet.update, feed_dict={Qnet.input:np.vstack(ex_batch[:,0]),Qnet.target_y:y, Qnet.a:ex_batch[:,1]})   # input is s not s1
                istrain = 1  # try
            	

            if total_step % updata_f == 0:    # copy weights from Qnet to Targetnet
                #print("we copy weights from Qnet to Targetnet")
                update_net(trainable_var, sess)
                isupdate = 1 # try
                update_num = update_num + 1
            #testt.append([test, action, istrain, isupdate])  # try
                
            if d == True:
                print("True exame")
                print(abs(env.next_position[0] - env.end_position[0])) 
                print("stride_height: ",env.stride_height) 
                print(abs(env.next_position[1] - env.end_position[1])) 
                print("stride_wide: ",env.stride_wide)
                print("-----###")
                print("Success")
                if in_ep_step > max_step:  # we don't want to much step
                    step_buffer = []
                if in_ep_step > 0:
                    avg_loss = in_ep_loss / in_ep_step
                real_reward = episode_reward + 0.1 * (in_ep_step - env.unreach_position_num) - 1   # We don't penalize transition for real_reward(compare with google route)
                real_r_nofail = real_reward + env.unreach_position_num
                #print("Reach end")
                print("Step to reach end: ", in_ep_step)
                #print("current position: ", env.current_position)
                battery.append([charge_num, SOC])  # SOC is the current one
                #print("charging routine: ", battery[-1])
                time = env.time
                history = [episode+1, in_ep_step, time, episode_reward, real_reward, real_r_nofail, charge_num, SOC, env.unreach_position_num, d, random_a/(random_a+network_a), avg_loss, overQ_num, loss_history, step_buffer]
                if episode == 0:                    
                    df = pd.DataFrame([history])
                    df.to_csv("./ev/result.csv", header=["episode", "step", "time", "reward", "reward_notrain", "reward_nofail", "charge_num", "SOC", "unreach_position", "Reach", "Random_a", "Avg_loss", "overQuery_num", "Loss history", "Step history"])
                    tt = tt + 1
                elif episode > 0:
                    with open('./ev/result.csv', 'a') as f:
                        df = pd.DataFrame([history])
                        df.to_csv(f, header=False)
                print("Total time: ", time)
                print("number of failed step: ", env.unreach_position_num)
                
                env.time = 0 # reset time
                #env.charge_num = 0  # reset the charging number
                env.unreach_position_num = 0
                if in_ep_step < total_point/2:
                    print("Google route info >>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                    print("realp_reward, chargenum, SOC, time: ", step_rewardG, chargenumG, SOCG, timeG)
                    print("Our route step less than"+ str(total_point/2) + "  >>>>>>>>>>>>>>>>>>>")
                    print("Summary: ", real_r_nofail, charge_num, SOC, time)
                    
                break

            if d == False and in_ep_step == max_step:
                #step_buffer = []
                if in_ep_step > 0:
                    avg_loss = in_ep_loss / in_ep_step   # average loss in one episode
                #print("testt [test, action, istrain, isupdate]: ", testt)  # try
                print("Failed")
                time = env.time
                real_reward = episode_reward + 0.1 * (in_ep_step - env.unreach_position_num)  # We don't penalize transition for real_reward(compare with google route) and we don't count the goal 
                real_r_nofail = real_reward + env.unreach_position_num
                history = [episode+1, in_ep_step, time, episode_reward, real_reward, real_r_nofail, charge_num, SOC, env.unreach_position_num, d, random_a/(random_a+network_a), avg_loss, overQ_num, loss_history, step_buffer]
                if episode == 0:
                    df = pd.DataFrame([history])
                    df.to_csv("./ev/result.csv", header=["episode", "step", "time", "reward", "reward_notrain", "reward_nofail", "charge_num", "SOC", "unreach_position", "Reach", "Random_a", "Avg_loss", "overQuery_num", "Loss history", "Step history"])
                elif episode > 0:
                    with open('./ev/result.csv', 'a') as f:
                        df = pd.DataFrame([history])
                        df.to_csv(f, header=False)
                #env.current_position = env.start_position  # reset the start position to origine
                #s = env.start_position  # reset the start position to origine
                #s_list = list(s)
                env.time = 0  # reset time
                #env.charge_num = 0  # reset the charging number
                env.unreach_position_num = 0
                break
                
            #total_step = total_step + 1
            if overQ_num_roll > 50:
                overQ_num_roll = 0
                print("Sleeping within episode for 60 min")
                tm.sleep(3600)

        if d == True and in_ep_step < 60 and episode > 10 and episode % 1 == 0 or (load_model == True and d == True):
            j = episode + 1
            save_path = saver.save(sess, path+"/model-"+str(j)+".ckpt")
            print("Saved model with step less than steps 60")
            
        print("Last position: ", env.current_position)
        print("Destination: ", env.end_position)
        #print("env.next_position", env.next_position)
        #print("env.stride height(km): ", env.envheightkm)
        print("env.stridebound a, b", env.stridebounda, env.strideboundb)
        env.current_position = env.start_position  # reset the start position to origine
        #print("current position: ", env.current_position)
        s = env.start_position  # reset the start position to origine
        s_list = list(s)
        ss, nn = env.battery_condition()
        print("SOC, charge_number: ",ss,nn)
        env.charge_num = 0  # reset the charging number
        #total_step = total_step + 1
        reward_history.append(episode_reward)
        env.battery_charge()
        if total_step > 500 and total_step % 140 == 0 or sleep == True:
        #if total_step > 500 and (episode + 1) % 1 == 0 or sleep == True:
            print("Sleeping now for 20 min")
            tm.sleep(1230)
            #print("Sleeping now for 10 min")
        #print("total step: ", total_step)  # try
        print("-------------------------------------------------------------------------------")
    #print(step_buffer[:,2])
    #print(sess.run(trainable_var))
    print("______________Episode end___________________")





print("------------------End----------------")
#initialize two structure: https://stackoverflow.com/questions/41577384/variable-scope-issue-in-tensorflow
