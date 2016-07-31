% Tutorial
% Lujing Cen
% 7/30/2016

# Introduction

Are you trying to build a quadruped robot? Are you trying to understand code in this repository? If you answered yes to either question, you are in the right place. This tutorial will provide a comprehensive guide for building a quadruped robot while providing details on how important pieces of code in this repository function and relate to their conceptual counterparts.

### Warnings

This guide is in no way comprehensive. I am not accountable for errors in this document. Don't let this guide prevent you from thinking of new designs, concepts, and algorithms. Remember that I am no expert on this subject. Your ideas could very well be better than mine. At the same time, don't attempt to reinvent the wheel. If something is efficient and works for your purpose, use it.

"Premature optimization is the root of all evil." Test and measure. Don't guess.

### Read Me

While researching, I chanced upon the Springer Handbook of Robotics. Before proceeding, read section 16.5 of the book found [here](http://home.deib.polimi.it/gini/robot/docs/legged.pdf). If you are serious about robotics, I recommend that you find this book in the library or get an eBook. This book basically covers everything you need to know about advanced robotics and even provides historical background. You probably won't understand everything in this literature. That is completely okay. This is just an introduction.

### Prerequisites

Trying to accomplish this project requires that you are not scared of math and physics. You will need a strong foundation in geometry, trigonometry, algebra, classical mechanics, and prelimiary linear algebra. You will also need a deep understanding of calculus, although you might not ever need to take a derivative in this project. It would help that you also understand some practical electricity and magnetism.

# Definitions

It is important to define everything before starting this project. It will save you a lot of time. Don't invent your own coordinate system like me and waste 2 weeks :p.

### Coordinate System

The world runs on the right-handed coordinate system. Being left-handed, I accidentally used the left-handed coordinate system, which ended up causing me a lot of confusion. Don't be like me. Clearly define the coordinate system before beginning. This is not to say you can't use the left-handed system. Just make sure you know what you're doing, because pretty much everything on the internet uses the right-handed system.

![](assets/table.jpg)

Pretend the robot is a table. The head points in the positive x direction. The left side points in the positive y direction. The top of the table points to the positive z axis. The image is there for clarification.

### Vocabulary

End Effector
: In kinematics, the end of a robotic arm or leg. In this case, it is the tip of the feet.

Root
: In kinematics, the point at which the arm or leg attaches to the body.
	
