/**
* This file is part of ORB-SLAM2.
*
* Copyright (C) 2014-2016 Raúl Mur-Artal <raulmur at unizar dot es> (University of Zaragoza)
* For more information see <https://github.com/raulmur/ORB_SLAM2>
*
* ORB-SLAM2 is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* ORB-SLAM2 is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with ORB-SLAM2. If not, see <http://www.gnu.org/licenses/>.
*/


#include <iostream>
#include <algorithm>
#include <fstream>
#include <chrono>
#include <cstdlib>
#include <thread>

#include <opencv2/opencv.hpp>

#include <Tracking.h>
#include <Map.h>
#include <LoopClosing.h>
#include <LocalMapping.h>
#include <KeyFrameDatabase.h>
#include <System.h>


using namespace std;
using namespace ORB_SLAM2;


int main(int argc, char **argv)
{
	cv::VideoCapture capLeft("C:/users/bobbyluig/Desktop/00/image_0/%06d.png");
	cv::VideoCapture capRight("C:/users/bobbyluig/Desktop/00/image_1/%06d.png");

	TrackerParams params;
	params.sensor = System::MONOCULAR;
	params.fx = 718.856;
	params.fy = 718.856;
	params.cx = 607.1928;
	params.cy = 185.2157;

	params.fps = 30.0;
	params.RGB = false;

	ORBVocabulary mpVocabulary;
	bool bVocLoaded = mpVocabulary.loadFromTextFile2("C:/Users/bobbyluig/Documents/GitHub/Eclipse/src/theia/slam/python/voc.txt");
	if (!bVocLoaded)
		return -1;

	KeyFrameDatabase mpKeyFrameDatabase(mpVocabulary);
	Map mpMap;

	Tracking tracker1(mpVocabulary, mpMap, mpKeyFrameDatabase, params);
	Tracking tracker2(mpVocabulary, mpMap, mpKeyFrameDatabase, params);

	LocalMapping mpLocalMapper(mpMap, true);
	LoopClosing mpLoopCloser(mpMap, mpKeyFrameDatabase, mpVocabulary, false);

	tracker1.SetLocalMapper(mpLocalMapper);
	tracker2.SetLocalMapper(mpLocalMapper);
	tracker1.SetLoopCloser(mpLoopCloser);
	tracker2.SetLoopCloser(mpLoopCloser);

	mpLocalMapper.SetLoopCloser(mpLoopCloser);
	mpLoopCloser.SetLocalMapper(mpLocalMapper);

	mpLocalMapper.Run();
	mpLoopCloser.Run();

	for (int i = 0; i < 100; ++i)
	{
		cv::Mat first_img; 
		capLeft >> first_img;

		// cv::imshow("first", first_img);

		cv::Mat p = tracker1.GrabImageMonocular(first_img, 30);
		int state = tracker1.GetState();

		if (!p.empty())
			cout << i << " " << p.reshape(0, 1) << endl;
		else
			cout << i << " " << state << endl;

		cv::waitKey(1);
	}

	bool success = tracker2.ForceLocalize();
	assert(success);
	tracker2.InformOnlyTracking(true);

	for (int i = 0; i < 4440; ++i)
	{
		cv::Mat first_img;
		cv::Mat second_img;

		capLeft >> first_img;
		capRight >> second_img;

		cv::imshow("first", first_img);
		cv::imshow("second", second_img);

		cv::Mat p1 = tracker1.GrabImageMonocular(first_img, 30);
		int state1 = tracker1.GetState();

		if (!p1.empty())
			cout << "p1 " << i << " " << p1.reshape(0, 1) << endl;
		else
			cout << "p1 " << i << " " << state1 << endl;

		cv::Mat p2 = tracker2.GrabImageMonocular(second_img, 30);
		int state2 = tracker2.GetState();

		if (!p2.empty())
			cout << "p2 " << i << " " << p2.reshape(0, 1) << endl;
		else
			cout << "p2 " << i << " " << state2 << endl;

		cv::waitKey(1);
	}

	mpLocalMapper.RequestFinish();
	mpLoopCloser.RequestFinish();

	while (!mpLoopCloser.isFinished() || !mpLocalMapper.isFinished())
		this_thread::sleep_for(chrono::milliseconds(5));

	return 0;
}
