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


#ifndef SYSTEM_H
#define SYSTEM_H

#include <string>
#include <vector>
#include <map>
#include <utility>
#include <boost/thread.hpp>
#include <opencv2/core/core.hpp>

#include "Tracking.h"
#include "Map.h"
#include "LocalMapping.h"
#include "LoopClosing.h"
#include "KeyFrameDatabase.h"
#include "ORBVocabulary.h"


namespace ORB_SLAM2
{

	class Viewer;
	class FrameDrawer;
	class Map;
	class Tracking;
	class LocalMapping;
	class LoopClosing;

	class System
	{
	public:
		// Input sensor
		enum eSensor {
			MONOCULAR = 0,
			STEREO = 1,
			RGBD = 2
		};

	public:

		// Initialize the SLAM system. It launches the Local Mapping, Loop Closing and Viewer threads.
		System();
		~System();

		// Loading, starting, and stopping system threads.
		bool Load(const string &strVocFile);
		bool Start();
		void Stop();

		// Add tracker.
		bool BindTracker(Tracking &tracker);

		// Proccess the given monocular frame
		// Input images: RGB (CV_8UC3) or grayscale (CV_8U). RGB is converted to grayscale.
		// Returns the camera pose (empty if tracking fails).
		cv::Mat TrackMonocular(const cv::Mat &im, const double &timestamp);


	private:
		// Input sensor
		const eSensor mSensor = MONOCULAR;

		// ORB vocabulary used for place recognition and feature matching.
		ORBVocabulary* mpVocabulary;

		// Is running?
		bool isRunning;

		// KeyFrame database for place recognition (relocalization and loop detection).
		KeyFrameDatabase* mpKeyFrameDatabase;

		// Map structure that stores the pointers to all KeyFrames and MapPoints.
		Map* mpMap;

		// Tracker. It receives a frame and computes the associated camera pose.
		// It also decides when to insert a new keyframe, create some new MapPoints and
		// performs relocalization if tracking fails.
		map< int, pair<Tracking*, boost::thread*> > mpTrackers;

		// Local Mapper. It manages the local map and performs local bundle adjustment.
		LocalMapping* mpLocalMapper;

		// Loop Closer. It searches loops with every new keyframe. If there is a loop it performs
		// a pose graph optimization and full bundle adjustment (in a new thread) afterwards.
		LoopClosing* mpLoopCloser;

		// System threads: Local Mapping, Loop Closing, Viewer.
		// The Tracking thread "lives" in the main execution thread that creates the System object.
		boost::thread* mptLocalMapping;
		boost::thread* mptLoopClosing;
	};

}// namespace ORB_SLAM

#endif // SYSTEM_H
