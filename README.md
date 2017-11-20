# Electrical Vehicle Route Planning on Google Map with Reinforcement Learning
More datail please find the README.pdf experiment section

# Library Requirements with Python 3.6.2:
(1) Tensorflow (CPU)
(2) numpy
(3) pandas
(4) haversine
(5) time
(6) random
(7) math
(8) requests
(9) urllib

# How can you get start
(1) enter your start position: name of position or geocode (lat, lng)<br />
(2) enter your destination position: name of position or geocode (lat, lng)<br />
(3) enter the length of each step, higher but less accurate (ex: 1000m takes less time to train compare to 100m)<br />
(4) enter how many episode you want to train<br />

# How does this work
(1) Learning Environment<br />
Make the map like a grid map for the learning agent to navigate on (figure(a)). Strictly speaking, each grid in the grid map is not a rectangle. This phenomenon is caused by the sphere geometry and our restriction on the length of the stride which is demonstrated in figure (b)<br />
![gridmap](https://user-images.githubusercontent.com/25232370/33046405-c89e8556-ce1e-11e7-8f9a-ff50a931ccb5.JPG)<br />
(2) Interact with Google map API /><br />
assume that the agent is at current position denoted by A and heading south to the next position denoted by B. Apparently, the route provided by the Directions API is the highway 395 and the distance is longer than 1000m. We can get the navigating instruction list with the form: { geocode of A, duration from A to 1, distance from A to 1, geocode of 1 }, {geocode of 1, duration from 1 to 2, distance from 1 to 2, geocode of 2 }.... where A, 1, 2 ,3 , B are shown in figure 6 after we input the geocode of A and the geocode of B into the Directions API. The number of instruction is based on the Directions API and there are four instructions in our case of following figure from A to B. We use each of the geocode in the navigating instruction list to get the height of each position from the Elevation API and compute the elevation within each instruction.
![map1](https://user-images.githubusercontent.com/25232370/33046910-0d9b5b82-ce21-11e7-8974-4f9c0aa63e22.JPG)<br />


(3) Energy Computation<br /><br />
The following graph shows how to compute the energy for a vehicle to travel uphill (can also be applied on a flat road)<br />
![car2](https://user-images.githubusercontent.com/25232370/33047104-0e497efa-ce22-11e7-99f9-2452ec593348.JPG)<br />
But noticed that we only compute the elevation between the two position shown in the following graph. To increase the accuracy, you should minimize the distance between these two position (this will increase the computation time).<br />
![car1](https://user-images.githubusercontent.com/25232370/33046721-338fe5b6-ce20-11e7-8c17-3663462ac24f.JPG)<br />

(4)


# Result
![result](https://user-images.githubusercontent.com/25232370/33046240-25c5ac2e-ce1e-11e7-9156-faf109c42bbe.JPG)
