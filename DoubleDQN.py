import tensorflow as tf

class Qnetwork():
    def __init__(self, s_size, a_size):
        self.a_size = a_size
        self.s_size = s_size
        #self.layer_name = layer_name
        self.structure()


    def structure(self):
        init = tf.glorot_normal_initializer()
        self.input = tf.placeholder(dtype=tf.float32, shape=[None,self.s_size])
        self.inputt = tf.truediv(self.input,[[180.0,180.0]])
        self.W_1 = tf.get_variable(shape=[self.s_size,10], dtype=tf.float32, name='w1', initializer=init)
        self.b_1 = tf.get_variable(shape=[10], dtype=tf.float32, name='b1')
        h_1 = tf.nn.relu(tf.matmul(self.inputt, self.W_1) + self.b_1)
        self.h_1_drop = tf.nn.dropout(h_1, keep_prob=0.75)
        self.W_2 = tf.get_variable(shape=[10,6], dtype=tf.float32, name='w2', initializer=init)
        self.b_2 = tf.get_variable(shape=[6], dtype=tf.float32, name='b2')
        h_2 = tf.nn.relu(tf.matmul(h_1, self.W_2) + self.b_2)
        self.h_2_drop = tf.nn.dropout(h_2, keep_prob=0.75)
        self.W_3 = tf.get_variable(shape=[6, self.a_size], dtype=tf.float32, name='w3', initializer=init)
        self.action = tf.matmul(self.h_2_drop, self.W_3)   # Q value for each action
        self.predict = tf.argmax(input=self.action, axis=1)
        self.target_y = tf.placeholder(dtype=tf.float32, shape=[None])
        self.a = tf.placeholder(dtype=tf.int32, shape=[None])
        self.predict_onehot = tf.one_hot(indices=self.a, depth=4, on_value=1, off_value=0)
        self.floatpre = tf.cast(self.predict_onehot, tf.float32)
        #self.Q = tf.matmul(self.floatpre,self.action)
        self.Q = tf.reduce_sum(tf.multiply(self.floatpre,self.action), axis=1)   # Targetnet's Q value in batch
        self.error = tf.square(self.target_y - self.Q)
        self.loss = tf.reduce_mean(self.error)
        self.optimizer = tf.train.AdamOptimizer(learning_rate=0.0001)
        self.update = self.optimizer.minimize(self.loss)

