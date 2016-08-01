% Tutorial
% Lujing Cen
% 7/30/2016

# Introduction

Are you trying to build a quadruped robot? Are you trying to understand code in this repository? If you answered yes to either question, you are in the right place. This tutorial will provide a comprehensive guide for building a quadruped robot while providing details on how important pieces of code in this repository function and relate to their conceptual counterparts.

### Goal

The goal is to design a quadruped robot that looks like a dog. A lot of tutorials explain how to build a spider-looking quadruped. However, the concepts are exactly the same. This tutorial is intended to cover various mathematically and engineering concepts used in constructing the robot. It does not teach you how to build a robot step by step, nor should it be seen as such.

### Warnings

This guide is in no way comprehensive. I am not accountable for errors in this document. Don't let this guide prevent you from thinking of new designs, concepts, and algorithms. Remember that I am no expert on this subject. Your ideas could very well be better than mine. At the same time, don't attempt to reinvent the wheel. If something is efficient and works for your purpose, use it.

"Premature optimization is the root of all evil." Test and measure. Don't guess.

### Read Me

While researching, I chanced upon the *Springer Handbook of Robotics*. Before proceeding, read section 16.5 of the book found [here](http://home.deib.polimi.it/gini/robot/docs/legged.pdf). If you are serious about robotics, I recommend that you find this book in the library or get an eBook. This book basically covers everything you need to know about advanced robotics and even provides historical background. You probably won't understand everything in this literature. That is completely okay. This is just an introduction.

You should also read through the [SPS](https://github.com/bobbyluig/Eclipse/raw/master/docs/cdr/SPS.pdf) and [POC](https://github.com/bobbyluig/Eclipse/raw/master/docs/cdr/POC.pdf) documents. They provide comprehensive details on our robots. This tutorial goes in depth on what is not covered by those documents. You will be confused if you do not at least skim through them.

### Corrections

I will put errors in the documents here as I find them.

- Pg. 88-91: All references to dot products should be changed to matrix multiplcation. All $\bullet$ should be removed from the equations.

### Prerequisites

Trying to accomplish this project requires that you are not scared of math and physics. You will need a strong foundation in geometry, trigonometry, algebra, classical mechanics, and prelimiary linear algebra. You will also need a deep understanding of calculus, although you might not ever need to take a derivative in this project. It would help that you also understand some practical electricity and magnetism.

This tutorial is written assuming you have limited understanding of linear algebra. Concepts clarifications are linked to external resources as they appear. You're welcome.

# Definitions

It is important to define everything before starting this project. It will save you a lot of time. Don't invent your own coordinate system like me and waste 2 weeks :p.

### Coordinate System

The world runs on the right-handed coordinate system. Being left-handed, I accidentally used the left-handed coordinate system, which ended up causing me a lot of confusion. Don't be like me. Clearly define the coordinate system before beginning. This is not to say you can't use the left-handed system. Just make sure you know what you're doing, because pretty much everything on the internet uses the right-handed system.

![](assets/table.jpg)

Pretend the robot is a table. The head points in the positive x direction. The left side points in the positive y direction. The top of the table points to the positive z axis. The image is there for clarification.

### Vocabulary

End effector
: In kinematics, the end of a robotic arm or leg. In this case, it is the tip of the feet.

Root
: In kinematics, the point at which the arm or leg attaches to the body.
	
Output spline
: The part of the servo that is visible and spins. It has teeth to transfer torque.
	
# Leg Design

### Alignment

### Considerations

# Kinematics

This is perhaps the most math intensive and important portion of the project. The goal is to create two equations. One equation will take angles and output a point. The other will do the reverse. Sounds easy? It's not.

### Forward Kinematics

Forward kinematics (FK) is kind of like taking a derivative. There can be a lot of steps and it can get messy, but it's always possible. For the purpose of this tutorial, I will assume that each leg has three DOF, which is pretty standard. Each servo will have a $\theta$ value. The forward kinematic function $f(\theta_1, \theta_2, \theta_3)$ should output $(x, y, z)$, where the end effector is given the angles.

If you are good at trigonometry, FK can be solved starting from the servo closest to the body. An example can be seen [here](http://www.stagrobotics.com/stag.html). However, it does not have to be solved that way. You can also apply [rotational matrices](http://inside.mines.edu/fs_home/gmurray/ArbitraryAxisRotation/) when they are convenient to use. I've generalized the use of rotation matrices to be:

1. Check to see if you can ignore any segments. This can happen when the line formed by the segment is the axis of rotation for a servo attached to that segment.
2. Try to reduce the problem to a 2D one and use basic trignometry to consume one or more $\theta$s.
3. Apply rotational matrices via [matrix multiplcation](https://en.wikipedia.org/wiki/Matrix_multiplication) for any servos rotating about convenient axes.
4. Use trigonometry to solve for any remaining servos.

Use whichever method you find to be easier. Apply rotation matrices can be confusing. However, you will need to understand 3D trignomoetry to do it the other way. Remember -- draw a diagram, take it slow, and test your solution.

### Inverse Kinematics

Inverse kinematics (IK) is kind of like performing an integral. It involves some intuition and might not always be possible. Also, like an indefinite integral, more than one solution can exist. Be sure to solve the FK problem before approaching this one. 

IK should be solved from the servo furthest from the body. The last angle generally involves some form of the law of cosines. Once you solve one angle, see if you can plug it into any of the equations obtained from forward kinematics. The last part is mostly just intuition. You'll need to draw diagrams and model the leg somehow to help you visualize a solution. Take it slow. Solving the IK for my robot took me 2 weeks.

Remember that multiple solutions generally will exist. Anything involving the law of cosines can vary by $\pi$. Other trignometric expressions can involve solutions with different signs. Be aware of this. Try to design the program to find all possible solutoins. Write good tests that chain the working FK equations with the IK equations to rigorously test correctness.

There are software which you can use. If you do manage to obtain a non-manual solution, be sure that it can be evaulated very quickly.

### Code

Only one class controls the kinematics modules. The evaluation speed must be very fast or else real time performance will not be achieved.

Concept|Implementation(s)
:---|---
Forward Kinematics | `finesse.eclipse.Finesse.forward_pack`, `finesse.paragon.Finesse.forward_pack`
Inverse Kinematics | `finesse.eclipse.Finesse.inverse_pack`, `finesse.paragon.Finesse.inverse_pack`

# Servos

Servos are what permits motion. More sophisticated robots make use of pneumatics. However, hobby servos can perform well with proper design and programming.

### Configuration

Servos generally come with information about their [Pulse Width Modulation](https://en.wikipedia.org/wiki/Pulse-width_modulation) (PWM). These typically range from 1000 μs to 2000 μs, although you need to check the manufacturer's specification sheet as well as perform testing to determine the true PWM range.

I will not cover conversion from PWM to degrees, as I'm sure you can figure this out by either looking at the code or doing some math. The more interesting question is which direction is positive and which direction is negative in regards to the spin of the servos.

![](assets/servo.png)

We need to first define that lowering the PWM corresponds to decreasing the angle of the servo. Given that definition, it is simple to determine spin direction based on servo configuration. Look down the positive axis. In the image above, the eye is looking down the positive y axis. If the output spline is facing you (as in the image), then counterclockwise is positive and clockwise is negative. If the output spline is facing the other way, then the directions are flipped. However, both cases assume that the servo body is not the part rotating. If the output spline is attached and the body spins, everything is reversed.

Of course, there are multiple ways to implement this. In my implementation, if the output spline points towards a positive axis, it has a `direction` of 1. If it points towards a negative axis, it has a `direction` of -1. All other parameters are commented in the source code and should be easy to understand.

### Alternatives

Servos can target a specific location, but often has limited range and requires calibration after mounting. An alternative would be to use stepper motors. These motors run on two inductors. They have hundreds of clicks per rotation and each pulse will move the stepper one click in a specified direction. This allows easier calibration and better synchronization at the cost of torque and speed.

I have actually implemented a class for this. However, my team never managed to get the stepper motors working without burning them out. In addition, we lacked funds to get small steppers with sufficient torque.

### Code

There are two classes, one for servos and another for steppers. The `Stepper` class has not been tested extensively. Some functions in the `Servo` class are not used. They were written when I was testing different gait generation methods. However, they do work as expected and can be useful.

Concept|Implementation(s)
:---|---
Servo | `agility.main.Servo`
Stepper | `agility.main.Stepper`

# Mini Maestro

### Protocol

### USC

### Synchronization

### Code

# Movement

We want to translate user inputs of rotational motion ($rad / sec$) and forward motion ($cm / sec$) to physical robot motion. The first challenge is to use $d\theta$, the amount of rotation per cycle, and $dv$, the amount of forward motion per cycle, to generate proper gaits. The second challenge is to perform various gait optimizations to ensure that the robot walks smoothly. Note: this section is very math heavy.

### Vectors

My friend Alastair MacMillan came up with this amazing idea one day that basically made complex motion possible. For a moment, pretend that the robot is just a rectangle.

<div class="center">
![](assets/vector.png)\ ![](assets/vector1.png)
</div>

The verticies or legs are number 0-3 accordingly. To rotate the rectangle, we can simply apply a vector tangent to a circumscribed circle at each vertex. The cool thing about vectors is that they can be view as separate components. To add forward or backward movement, simply add to the x component.

The easiest method to physically reproduce the vector is to compute $(x, y)$ and generate a line between $(x, y)$ and $(-x, -y)$. Moving one cycle along the line will be twice the desired vector. 

The harder part is using $\theta$ to find $x$ and $y$. At every instantaneous moment in time, each leg applies a force. Relative to their respective roots the force is linear over time. However, when all four legs work together, the linear force becomes rotational. 

![](assets/vector2.png)

We define the width $w$ to be the distance along y and length $l$ to be the distance along x. Let $u$ be a matrix or width and length. The magnitude of the vector is defined to be $|\Delta|$ and the radius of the circle is $r$. A few things become immediately evident.

$$r = \frac{1}{2} \sqrt{w^2 + l^2}$$
$$|\Delta| = \sqrt{x^2 + y^2}$$
$$B = \begin{bmatrix} w \\ l \end{bmatrix}$$

$\theta$, how much the robot will turn when the leg moves $\Delta$, is between $r$ and the hypotenuse. It can be solved using inverse tangent.

$$\theta = \arctan \left(\frac{|\Delta|}{r}\right)$$

The desired theta input is twice of that. So the input $d\theta = 2 \theta$. We can then solve for $|\Delta|$.

$$|\Delta| = r \tan \left(\frac{1}{2} d\theta \right)$$

The $(x, y)$ contribution from the rotation part is always perpendicular to the line from the center to the vertex. This means that we can use the [normalized vector](https://en.wikipedia.org/wiki/Unit_vector) of $B$ to find the desired values. Finally, add the desired forward contribution value for $dv$. Signs for the result is computed using a [Hadamard product](https://en.wikipedia.org/wiki/Hadamard_product_(matrices)) and a predefined matrix $N$. Let $j$ be the index of the leg (0-3).

$$N = \begin{bmatrix} -1 & 1 & -1 & 1 \\ 1 & 1 & -1 & -1 \end{bmatrix}$$
$$\begin{bmatrix} x \\ y \end{bmatrix}_{j} = \left( |\Delta| \hat{B} + \begin{bmatrix}dv \\ 0 \end{bmatrix} \right) \circ N_{i,j+1}$$

I will expand this equation out for clarity, since it is very important for implementation.

$$x_{j} = r \tan \left(\frac{1}{2} d\theta \right) \sqrt{w^2 + l^2} \left(N_{1,j+1}\right)$$
$$y_{j} = r \tan \left(\frac{1}{2} d\theta \right) \sqrt{w^2 + l^2} \left(N_{2,j+1}\right)$$

### Gait Types

There are various gait types described in *Springer Handbook of Robotics*. However, I believe that trot and crawl are the two easier gaits to implement. Obviously, trot is much faster than crawl. However, testing should reveal the optimal transition speed and time. If both are graphed, if can be seen that this is an optimization problem. I did not have sufficient time to test thoroughly. However, if time $t$ can be found, it is easy to convert $rad / sec$ and $cm / sec$ to $d\theta$ and $dv$.

$$\begin{bmatrix} d\theta \\ dv \end{bmatrix} = t \begin{bmatrix} rad/sec \\ cm/sec \end{bmatrix}$$

I have not found significant differences between different leg orderings. However, this is because I have not done extensive testing. The robots use 1423 creeping gaits, although the other orderings work as well.

### Gait Generation

There are a few additional variables involved in gait generation. The variable $h$ defines how high the leg should lift and the variable $\beta$ determines the percent of time a leg is on the ground. My idea for gait generation was to have one gait per set of $(d\theta, dv)$. There are other ways to approach this of course.

Assuming that we have already computed the necessary $(x, y)$ value for the gait, we can go through a set of points and interpolate the data in between when needed. For the sake of simplicity, I designed all leg paths to be a rectangle. However, this may not be the most efficient method considering the natural leg path of quadrupeds such as dogs. I defined 5 points, although 4 should be sufficient. Note that $g$ is the desired ground level. It should be negative, but greater than the z value of the end effector in zero position. Basically, the legs should be slightly bent during motion, to ensure that all points can be reached.

$$(0, 0, g) \rightarrow (-x, -y, g) \rightarrow (-x, -y, g + h) \rightarrow (x, y, g + h) \rightarrow (x, y, g)$$

The interpolation should be defined for all time values. To do this, you can use the interpolation feature that comes with `scipy`. By generating time values for each point based on normalized distance traveled. I used linear, which I believe is best for this case. However, more circular gaits should probably employ cubic interpolation.

The next step is to apply the concepts of calculus and separate this gait into tiny $dt$ segments. Note that $t$ in this case would be the time for one complete cycle of the gait. This $dt$ value is really dependent on the speed of the servo controller and the servos themselves. Servos generally run at a 50 Hz loop, implying that $dt$ should be at least 20 ms. I have found that 20 ms - 100 ms work well.

By generating $t / dt$ linearly spaced time points, we can then evaluate them in our intepolation equations to obtain points for execution.

### Gait Execution

Execution requires interfacing with various other modules. Once points for all four legs are obtained, they can be fed one frame at a time to the inverse kinematics equations, which will provide angles for the servos. Each frame is exactly $dt$ long. There are two possible ways to approach this (that I've thought of). One way is to send the command to move all the servos and wait $dt$ before executing the next one. However, I've found that Python is not very good at keeping accurate time. Instead, I chose to check if all servos have reached their target before executing the next frame. This is actually slowered, as there is latency involved with checking and executing. Thus, one cycle will be slightly longer (probably negligible) than $t$.

There are various other layers of complexity that must be considered to ensure that the robot can actually walk smoothly. They are discussed in the next three sections.

### Center of Mass

If the gait is execute without any adjustments, the robot will not walk -- it will fall and stumble. This is due to the fact that the center of mass (COM) is not being adjusted. As you can see in the image, the COM must fall inside of the support triangle made by three legs for crawl gaits.

![](assets/com.png)

First, let's define a few things. Let $(c_x, c_y)$ be the COM of the robot in its current position. This can be simplified to a static value or computed using the positions of the legs. Let $(x_1, y_1)$ and $(x_2, y_2)$ be the locations of two support legs across from each other. In the image above, they would be legs 0 and 3.

The shortest path to the inside of the triangle is the perpendicular to the slope formed by the two support legs. We need to find where on the line is the closest to the COM. To do this, Alastair derived this equation, which took me a while to understand. It is basically a lot of $y = mx + b$ manipulations. Let $(x_0, y_0)$ be the point on the line we are interested in.

$$m = \frac{(y_2 - y_1)}{(x_2 - x_1)}$$
$$b = y_1 - m x_1$$
$$x_0 = \frac{x_0 + m y_0 - mb}{m^2 + 1}$$
$$y_0 = m x_0 + b$$

Do the order of the points matter? No. If you look at the code, it may appear that it does. However, the order is for other optimizations. If working with the trot gait, this is enough because the COM simply has to be on the line. I use the variable $\delta$ to indicate how much the body must move.

$$\delta_{x,trot} = x_0 - c_x$$
$$\delta_{y,trot} = y_0 - c_y$$

Optimally, this would work for crawl as well. However, it would be even better to move the COM further into the support triangle. I used $\sigma$ to represent the safety margin. Rather than adjusting to a point on the line, the robot will move into the support triangle an aditional $\sigma$. There is a flaw in this because $\sigma$ is **not** the stability margin. When close to the sides of the triangle, it may be possible that moving $\sigma$ may cause the stability margin to be less than $\sigma$ on another side. It is even possible that the adjustment can throw the COM outside of the support triangle. I have not written in any protection for this as it usually is not a problem. However, this is definitely something to think about for improving motion.

Interestingly, order matters here with $\sigma$. I believe there is another way but this is just my take on it, since was really short on time. Which point comes first and which comes second depends on which leg is lifted. Testing basically reveals the following.

$$0: (2,1)$$
$$1: (0,3)$$
$$2: (3,0)$$
$$3: (1,2)$$

The following equations can then be applied to find $\delta$ for crawl gait. It basically uses trigonometric properties of perpendicular lines. Note that you must use the `atan2` function in your favorite programming language because signs are very important here. Also note that these are implemented **incorrectly** in the actual code (forgot to sutract COM). But hey, it still worked alright because I set a huge $\sigma$.

$$\DeclareMathOperator{\atantwo}{atan2}$$
$$\theta = \atantwo \left((y_2 - y_1),(x_2 , x_1) \right)$$
$$\delta_{x,crawl} = \sigma \sin \left( \theta \right) + x_0 - c_x$$
$$\delta_{y,crawl} = -\sigma \cos \left( \theta \right) + y_0 - c_y$$

I did static COM computations for $(c_x, c_y)$, but you should use the inverse kinematics equations to compute the location of each segement of the leg and use it to produce a more accurate computation. The servos are actually relatively heavy so the leg positions visibly contribute to the COM.

### Static Optimization

Adjustments to the gait can be made before execution. This is especially true with the COM. All operations rely on the use of `numpy`, which basically vectorizes operations in C. Because gait generation is called frequently, other programming optimizations such as caching should be used as well.

We'll redefine $\delta$ to be a 4 x 3 matrix rather than individual values of $\delta_x$, $\delta_y$, and $\delta_z$ (0). Let $F$ be a 4 x 3 matrix such that each row $i$ contains an $(x, y, z)$ which indicates the target position of leg at index $i - 1$.

$$\delta = \begin{bmatrix}
\delta_x & \delta_y & 0 \\
\delta_x & \delta_y & 0 \\
\delta_x & \delta_y & 0 \\
\delta_x & \delta_y & 0
\end{bmatrix}$$
$$F = \begin{bmatrix}
x_{0} & y_{0} & z_{0} \\
x_{1} & y_{1} & z_{1} \\
x_{2} & y_{2} & z_{2} \\
x_{3} & y_{3} & z_{3}
\end{bmatrix}$$

Remember that $\delta$ is how much the body has to move while $F$ is the position of the legs. To translate the body, we can simply apply Newton's third law of motion.

$$F^\prime = F - \delta$$

The optimized pose for the legs, $F^\prime$, is obtained by subtracting $\delta$ from every row of $F$. This is easy in `numpy`, as it supports automatically broadcasting arrays of different dimensions together. You can simply let $\delta$ be a 1 x 3 matrix instead when programming.

Initially, I added an additional optimization to crawl gait which involved rotating the body about the line produced by $(x_1, y_1)$ and $(x_2, y_2)$ away from the lifted leg. This lowers the COM, which improves stability. However, the tilting was causing too much shake to the camera, so I took it out. It may be useful to you, so I'll include some basic information here. 

We can use the [Euler–Rodrigues formula](https://en.wikipedia.org/wiki/Euler%E2%80%93Rodrigues_formula) to generate a rotation matrix. I took the code for it off of [StackOverflow](http://stackoverflow.com/questions/6802577/python-rotation-of-3d-vector). The function, when given an axis and angle, will generate a 3 x 3 matrix that I'll call $Q$. To apply this rotation to the aforementioned 4 x 3 matrix, we use a [matrix multiplcation](https://en.wikipedia.org/wiki/Matrix_multiplication) along with a [transpose](https://en.wikipedia.org/wiki/Transpose).

$$F^{\prime\prime} = F^\prime Q^T$$

COM adjustments don't need to occur when the robot is on four legs. Thus, modifing $F$ is only necessary on three legs. However, this algorithm can be jerky because the robot has to shift the COM rapidly in a single $dt$ segment. I've had a servo burn out because of this problem. A better algorithm would preemptively transition the COM even when the robot is on four legs so that it does not need to jerk when a leg lifts. Implementation involves looking at when all four legs are on the ground and when they are not. Then, simply run a smoothing algorithm that takes a large adjustment $\delta$ and breaks it up over multiple $dt$ frames.

Does it get more complicated? Of course! At higher speeds, $\delta$ can actually cause significant acceleration on the body. With acceleration in play, the COM is no longer crucial. Instead, the [zero moment point](https://en.wikipedia.org/wiki/Zero_moment_point) (ZMP) must fall inside of the support triangle. With no acceleration, the ZMP is equal to the COM. However, with acceleration, it gets really fun. See [this paper](http://dspace.mit.edu/openaccess-disseminate/1721.1/59530) for more information.

But wait, if you adjust for the ZMP, doesn't that also create another different acceleration that you have to optimize? You see, it gets very complicated. Using ZMP is necessary for bipedal robots and could improve quadrupedal walking a lot. However, it is way beyond my level of understanding. Feel free to look into it if you have time.

### Pose Optimization

Say you wanted the robot to get from its current pose to another pose. However, you don't want it to fall over of drag its legs on the ground. This is where pose optimization comes. Theoretically, pose optimization should allow the robot to get from any valid pose to any other valid pose.

The first step would be to use forward kinematics equations to determine the current location of all the legs. Then, move the body and lift the legs one at a time until all are in the correct location. Whenever a leg lifts, perform static optimizations. The logic is actually a bit more complex that, but the source code and comments could explain more clearly than words because there is no new math involved.

### Dynamic Optimization

These optimizations are done while the robot is running. However, I did not have time to implement them. Dynamic optimizations require the use of pressure sensors on the feet or at least an intertial measurement unit (IMU). As I have no implementation, I will simply provide some thoughts in this section.

Foot sensors will allow the robot to determine if it is falling in one direction or if it has a foot hold. It can be used to traverse uneven terrain. For example, if there is decreasing force on one feet when not expected, the robot may be tilting away from the feet.

An IMU can be fused to find the orientation of the robot. Combine this with raw acceleration data and you can find out if the robot is falling or about to fall. Acceleration is more useful in computing the ZMP in real time. If you do manage to get this data, you can use it to compute the ZMP and dynamically adjust the robot during motion. Assuming the COM remains at a constant height, then the ZMP, $z$, can be computed using the COM $(c_x, c_y, c_z)$ and the acceleration of the COM $(a_x, a_y, a_z)$.

$$z_x = \frac{c_x g - c_z a_x}{g}$$

This also applies for $z_y$. Again, this is just math. Actual implementation may require significant tweaking.

### Code

Multiple classes are involved in motion. A few functions in the `Agility` class are outdated and were used for testing. Other functions which relate to the head are discussed later.

Concept|Implementation(s)
:---|---
Vectors| `agility.gait.Dynamic.get`
Gait Types|	`agility.gait.Dynamic.generate`
Gait Generation| `agility.gait.Linear.interpolate`, `agility.gait.Dynamic.get`
Gait Execution| `agility.main.Agility.execute_frames`, `agility.main.Agility.execute_long`, `agility.main.Agility.execute_forever`, `agility.main.Agility.execute_angles`, `agility.main.Agility.execute_variable`
Center of Mass| `agility.main.Body.rotation_matrix`, `agility.main.Body.tilt_body`, `agility.main.Body.closest`, `agility.main.Body.adjust_crawl`, `agility.main.Body.adjust_trot`
Static Optimization | `agility.main.Agility.prepare_frames`, `agility.main.Agility.prepare_gait`, `agility.main.Agility.prepare_smoothly`
Pose Optimization| `agility.main.Agility.target_pose`, `agility.main.Agility.get_pose`

# Vision

### Tracking

### Detection

### SLAM

### Optimization

### Head

### Code

# Audio

### Concepts

### Code

# Automation

### Synthesis

### Decision Making

### Code

# Communication

### Workers

### Networking

### Code

# Control

### Considerations

### Code

# Material Selection

### Body

### Legs

# Component Selection

### Servos

### Steppers

### Microcontroller

### Battery

### Camera

# Electrical

### Amperage Draw

### Safety

### Battery
