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

#include "System.h"
#include "Converter.h"
#include <thread>
#include <iostream>     // std::cout, std::fixed
#include <iomanip>		// std::setprecision

namespace ORB_SLAM2
{

	System::System() : isRunning(false) {}

	System::~System()
	{
		Stop();

		delete mpKeyFrameDatabase;
		delete mpMap;
		// delete mpTrackers[0];
		delete mpLocalMapper;
		delete mptLocalMapping;
		delete mpLoopCloser;
		delete mptLoopClosing;
	}

	bool System::Load(const string &strVocFile)
	{
		mpVocabulary = new ORBVocabulary();

		bool bVocLoad = mpVocabulary->loadFromTextFile2(strVocFile);
		if (!bVocLoad)
			return false;

		// Create KeyFrame Database
		mpKeyFrameDatabase = new KeyFrameDatabase(*mpVocabulary);

		//Create the Map
		mpMap = new Map();

		//Initialize the Local Mapping thread
		mpLocalMapper = new LocalMapping(mpMap, mSensor == MONOCULAR);

		//Initialize the Loop Closing thread
		mpLoopCloser = new LoopClosing(mpMap, mpKeyFrameDatabase, mpVocabulary, mSensor != MONOCULAR);

		return true;
	}

	bool System::Start()
	{
		if (!mpLocalMapper || !mpLoopCloser)
			return false;

		// Run threads.
		mptLocalMapping = new std::thread(&ORB_SLAM2::LocalMapping::Run, mpLocalMapper);
		mptLoopClosing = new std::thread(&ORB_SLAM2::LoopClosing::Run, mpLoopCloser);

		// Have threads reference each other.
		mpLocalMapper->SetLoopCloser(mpLoopCloser);
		mpLoopCloser->SetLocalMapper(mpLocalMapper);

		// Toggle flag.
		isRunning = true;

		return true;
	}

	bool System::BindTracker(Tracking &tracker)
	{
		if (!isRunning)
			return false;

		tracker.Initialize(mpVocabulary, mpMap, mpKeyFrameDatabase, mpLocalMapper, mpLoopCloser);
		return true;
	}

	cv::Mat System::TrackMonocular(const cv::Mat &im, const double &timestamp)
	{
		// Check mode change
	{
		/*
		std::unique_lock<std::mutex> lock(mMutexMode);
		if (mbActivateLocalizationMode)
		{
			mpLocalMapper->RequestStop();

			// Wait until Local Mapping has effectively stopped
			while (!mpLocalMapper->isStopped())
			{
				//usleep(1000);
				std::this_thread::sleep_for(std::chrono::milliseconds(1));
			}

			mpTrackers[0]->InformOnlyTracking(true);
			mbActivateLocalizationMode = false;
		}
		if (mbDeactivateLocalizationMode)
		{
			mpTrackers[0]->InformOnlyTracking(false);
			mpLocalMapper->Release();
			mbDeactivateLocalizationMode = false;
		}
		*/
	}

	// Check reset
	{
		/*
		std::unique_lock<std::mutex> lock(mMutexReset);
		if (mbReset)
		{
			mpTrackers[0]->Reset();
			mbReset = false;
		}
		*/
	}

	// return mpTrackers[0]->GrabImageMonocular(im, timestamp);
	return cv::Mat();
	}

	void System::Stop()
	{
		mpLocalMapper->RequestFinish();
		mpLoopCloser->RequestFinish();

		// Wait until all thread have effectively stopped
		while (!mpLocalMapper->isFinished() || !mpLoopCloser->isFinished() || mpLoopCloser->isRunningGBA())
			std::this_thread::sleep_for(std::chrono::milliseconds(5));
		
		isRunning = false;
	}

} //namespace ORB_SLAM
