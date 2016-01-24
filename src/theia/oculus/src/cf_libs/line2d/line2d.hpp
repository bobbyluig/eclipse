#ifndef LINE2D_
#define LINE2D_

#include <boost/python.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>

#include <memory>
#include <chrono>
#include <iostream>
#include <fstream>
#include <stdlib.h>
#include <stdio.h>
#include <vector>

#include "linemod.hpp"
#include "gil.hpp"

using namespace boost::python;
using namespace std;

namespace template_match
{
	struct Line2DParameters
	{
		float weakThreshold = 10.0;
		int numFeatures = 63;
		float strongThreshold = 55.0;
		vector<int> pyramid = { 5, 8 };
	};

	class Line2D
	{
	public:
		Line2D(Line2DParameters paras)
			: _WEAK_THRESHOLD(paras.weakThreshold),
			_NUM_FEATURES(paras.numFeatures),
			_STRONG_THRESHOLD(paras.strongThreshold),
			_PYRAMID(paras.pyramid)
		{
			initialize();
		}

		int addTemplate(const cv::Mat& templ, const string& class_id)
		{
			releaseGIL unlock;

			vector<cv::Mat> templates;
			templates.push_back(templ);

			return _detector->addTemplate(templates, class_id, cv::Mat());
		}

		void removeTemplate(const string& class_id, const int template_id)
		{
			releaseGIL unlock;

			_detector->removeTemplate(class_id, template_id);
		}

		void removeClass(const string& class_id)
		{
			releaseGIL unlock;

			_detector->removeClass(class_id);
		}

		vector<cv::linemod::Match> match(const cv::Mat& image, float threshold)
		{
			releaseGIL unlock;

			vector<cv::Mat> sources;
			sources.push_back(image);

			vector<cv::linemod::Match> matches;
			_detector->match(sources, threshold, matches);

			return matches;
		}

		string exportTemplate(const string& class_id, const int template_id)
		{
			releaseGIL unlock;

			cv::FileStorage fs("temp", cv::FileStorage::WRITE | cv::FileStorage::MEMORY);
			_detector->writeTemplate(class_id, template_id, fs);
			string serializedString = fs.releaseAndGetString();
			return serializedString;
		}

		int importTemplate(const string& data)
		{
			releaseGIL unlock;

			cv::FileStorage fs(data, cv::FileStorage::READ | cv::FileStorage::MEMORY);
			cv::FileNode n = fs.root();
			return _detector->readTemplate(n);
		}

		string exportClass(const string& class_id)
		{
			releaseGIL unlock;

			cv::FileStorage fs("temp", cv::FileStorage::WRITE | cv::FileStorage::MEMORY);
			_detector->writeClass(class_id, fs);
			string serializedString = fs.releaseAndGetString();
			return serializedString;
		}

		string importClass(const string& data)
		{
			releaseGIL unlock;

			cv::FileStorage fs(data, cv::FileStorage::READ | cv::FileStorage::MEMORY);
			cv::FileNode n = fs.root();
			return _detector->readClass(n);
		}

		int numTemplates()
		{
			return _detector->numTemplates();
		}

		int numTemplatesInClass(const string& class_id)
		{
			return _detector->numTemplates(class_id);
		}

		int numClasses()
		{
			return _detector->numClasses();
		}

	private:
		void initialize()
		{
			vector< cv::Ptr<cv::linemod::Modality> > modalities;
			modalities.push_back(cv::makePtr<cv::linemod::ColorGradient>(_WEAK_THRESHOLD, _NUM_FEATURES, _STRONG_THRESHOLD));
			_detector = cv::makePtr<cv::linemod::Detector>(modalities, _PYRAMID);
		}

		cv::Ptr<cv::linemod::Detector> _detector;

		const float _WEAK_THRESHOLD;
		const int _NUM_FEATURES;
		const float _STRONG_THRESHOLD;
		const vector<int> _PYRAMID;
	};
}

#endif